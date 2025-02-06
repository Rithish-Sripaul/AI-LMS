import os
import datetime
from datetime import datetime as dt
import math
import requests
import io

from flask import render_template, send_file, redirect, request, url_for, Blueprint, flash, session, make_response, jsonify, Response
from flask_login import (
    current_user,
    login_user,
    logout_user
)

import pymongo
from database import get_db
from authentication import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId

import gridfs
from gridfs import GridFS

from pypdf import PdfReader
import ocrmypdf

from langchain_ollama import ChatOllama, OllamaLLM
from langchain_core.messages import AIMessage
import json

bp = Blueprint("quiz", __name__, url_prefix="")
llm = OllamaLLM(
    model="llama3.2",
    base_url="https://4e68-115-241-193-70.ngrok-free.app",
    temperature=0,
)


ollama_base_url = "https://4e68-115-241-193-70.ngrok-free.app"  # Replace <REMOTE_SERVER_URL> with your server's base URL
chatllm = ChatOllama(model="llama3.2", base_url=ollama_base_url)

conversation_history = []  # List to store user and bot messages


@bp.route("/quiz/adminHome", methods=["GET", "POST"])
@login_required
def adminHome():

  db = get_db()
  document_collection = db["documents"]
  topic_collection = db["topic"]
  quiz_head_collection = db["quiz_head"]
  quiz_questions_collection = db["quiz_questions"]

  # Get the list of quized made by this user
  quizzesList = list(quiz_head_collection.find({"uploaded_by": ObjectId(session["user_id"])}).sort({"uploaded_at": -1}))
  print(quizzesList)
  # Get the list of existing documents sort by alphabetically
  documentsList = list(
    document_collection.find({}).sort({"title": 1})
  )

  # Get the list of parent topic
  parentTopicList = list(
    topic_collection.find({"isSubTopic": False}).sort({"name": 1})
  )

  # Get the list of sub parent topic
  subParentTopicList = list(
    topic_collection.find({"isSubTopic": True}).sort({"name": 1})
  )

  if request.method == "POST":
    # Get the form data
    quizTitle = request.form["quiz_title"]
    subject = request.form["subject"]
    number_of_questions = request.form["no_of_questions"]
    time_limit = request.form["time_limit"] # in minutes

    # Lesson or topic
    lessonOrTopic = request.form["content_from"]

    if lessonOrTopic == "1":
      # LESSONS
      document_ids = request.form.getlist("document_id[]")
      print(document_ids)
      content = []
      lesson_names = []
      for document_id in document_ids:
        document_summary = document_collection.find_one({"_id": ObjectId(document_id)})["content"]
        lesson_names.append(document_collection.find_one({"_id": ObjectId(document_id)})["title"])
        content.append(document_summary)
      content = " ".join(content)

      quiz_head_metadata = {
        "uploaded_by": ObjectId(session["user_id"]),
        "title": quizTitle,
        "subject": ObjectId(subject),
        "number_of_questions": number_of_questions,
        "time_limit": time_limit,
        "type": "lesson",
        "lesson_names": lesson_names,
        "content": content,
        "uploaded_at": dt.now(),
      }
    else:
      # TOPICS
      topic_id = request.form["topic_id"]
      sub_topic_id = request.form["sub_topic"]
      if sub_topic_id == "":
        documents = document_collection.find({"topic_id": ObjectId(topic_id)})
      else:
        documents = document_collection.find({"sub_topic_id": ObjectId(sub_topic_id)})
      content = []
      for document in documents:
        content.append(document["content"])
      content = " ".join(content)

      quiz_head_metadata = {
        "uploaded_by": ObjectId(session["user_id"]),
        "title": quizTitle,
        "subject": ObjectId(subject),
        "number_of_questions": number_of_questions,
        "time_limit": time_limit,
        "type": "topic",
        "topic_id": topic_id,
        "sub_topic_id": sub_topic_id,
        "content": content,
        "uploaded_at": dt.now(),
      }
    
    # Save the quiz head metadata
    quiz_head_metadata_id = quiz_head_collection.insert_one(quiz_head_metadata).inserted_id

    # Generating the quiz questions
    # Get the content
    content = quiz_head_metadata["content"]
    number_of_questions = int(quiz_head_metadata["number_of_questions"])
    mcqPrompt = f"""
    Generate {number_of_questions} multiple-choice questions (MCQs) on the content: "{content}".
    ### **Instructions:**
    - Generate exactly **{number_of_questions}** MCQs based on the provided content.
    - Each MCQ should be **clear, well-structured, and non-repetitive**.
    - Ensure that questions **test understanding**, not just recall.
    - Provide **four answer choices** (`option_1` to `option_4`), making them **plausible yet distinct**.
    - Ensure **one correct answer**, marked as `correct_option` (1, 2, 3, or 4).

    Provide the output strictly in JSON format with the following structure:

    [
      {{
        "id": "<unique_question_id>",
        "quiz_head_id": "{quiz_head_metadata_id}",
        "question": "<Generated MCQ Question>",
        "option_1": "<First Option>",
        "option_2": "<Second Option>",
        "option_3": "<Third Option>",
        "option_4": "<Fourth Option>",
        "correct_option": "<Correct Option Number (1/2/3/4)>"
      }},
      ...
    ]
    Ensure that the questions are diverse and relevant to the topic. Include the correct_option as well. Give me only the JSON.
    """
    jsonQuiz = llm.invoke(mcqPrompt)
    questionsJSON = json.loads(jsonQuiz)
    for question in questionsJSON:
      question["quiz_head_id"] = quiz_head_metadata_id
      quiz_questions_collection.insert_one(question)
    
    return redirect(url_for("quiz.adminHome"))

  return render_template(
    "quiz/adminHome.html",
    documentsList=documentsList,
    parentTopicList=parentTopicList,
    subParentTopicList=subParentTopicList,
    quizzesList=quizzesList,
  )

@bp.route("/quiz/quizDetails/")
@bp.route("/quiz/quizDetails/<id>")
@login_required
def quizDetails(id=None):
  backPageUrl = "quiz.adminHome"
  db = get_db()
  user_collection = db["users"]
  quiz_head_collection = db["quiz_head"]
  quiz_questions_collection = db["quiz_questions"]

  quiz_head_id = ObjectId(id)
  quiz_head = quiz_head_collection.find_one({"_id": ObjectId(quiz_head_id)})
  quiz_questions = list(quiz_questions_collection.find({"quiz_head_id": ObjectId(quiz_head_id)}))

  uploadedBy = user_collection.find_one({"_id": quiz_head["uploaded_by"]})["username"]
  uploadedByEmail = user_collection.find_one({"_id": quiz_head["uploaded_by"]})["email"]


  return render_template(
    "quiz/quizDetails.html",
    quiz_head=quiz_head,
    quiz_questions=quiz_questions,
    uploadedBy=uploadedBy,
    uploadedByEmail=uploadedByEmail,
  )

@bp.route("/quiz/enrollStudents/", methods=["GET", "POST"])
@login_required
def enrollStudents():
  backPageUrl = "quiz.adminHome"
  
  db = get_db()
  user_collection = db["users"]
  topic_collection = db["topic"]

  # Get the list of parent topic
  parentTopicList = list(
    topic_collection.find({"isSubTopic": False}).sort({"name": 1})
  )

  # Get the list of Non admin users
  nonAdminUsers = list(
    user_collection.find({"isAdmin": False}).sort({"username": 1})
  )

  topicStudentList = list(
      topic_collection.aggregate([
          {
              "$lookup": {
                  "from": "users",               # Join with users collection
                  "localField": "students",      # Field in topic_collection (array of ObjectIds)
                  "foreignField": "_id",         # Corresponding field in users
                  "as": "student_details"        # Store result as 'student_details'
              }
          },
          {
              "$set": {
                  "student_details": {
                      "$sortArray": {
                          "input": "$student_details", 
                          "sortBy": { "username": 1 }  # Sort students alphabetically
                      }
                  }
              }
          },
          {
              "$project": {
                  "name": 1,                     
                  "student_details.username": 1   # Include student usernames
              }
          }
      ])
  )
  print(topicStudentList)

  if request.method == "POST":
    # Get the form data
    topic_id = request.form["topic_id"]
    topic = topic_collection.find_one({"_id": ObjectId(topic_id)})
    user_id = request.form["student"]
    user = user_collection.find_one({"_id": ObjectId(user_id)})


    # Add the student to the list of students under the topic
    topic_collection.update_one(
      {"_id": ObjectId(topic_id)},
      {"$push": {"students": ObjectId(user_id)}}
    )
    # adding the teacher to the student's list of teachers
    user_collection.update_one(
      {"_id": ObjectId(user_id)},
      {"$push": {"teachers": ObjectId(session["user_id"])}}
    )


    return redirect(url_for("quiz.enrollStudents"))

  return render_template(
    "quiz/enrollStudents.html",
    parentTopicList=parentTopicList,
    nonAdminUsers=nonAdminUsers,
    topicStudentList=topicStudentList,
  )

@bp.route("/quiz/takeQuiz/", methods=["GET", "POST"])
@login_required
def takeQuiz():
  db = get_db()
  topic_collection = db["topic"]
  quiz_head_collection = db["quiz_head"]
  quiz_questions_collection = db["quiz_questions"]

  user_id = ObjectId(session["user_id"])

  # Get the quizzes the user has already attended
  user = db.users.find_one({"_id": user_id}, {"attended_quizzes": 1})
  attended_quizzes = user.get("attended_quizzes", [])

  pipeline = [
      # Step 1: Find topics where the user is enrolled
      {"$match": {"students": user_id}},
      
      # Step 2: Lookup quizzes that match the topic ID
      {
          "$lookup": {
              "from": "quiz_head",
              "localField": "_id",
              "foreignField": "subject",
              "as": "quizzes"
          }
      },

      # Step 3: Unwind quizzes to process them individually
      {"$unwind": "$quizzes"},
      
      # Step 4: Exclude quizzes the user has already attended
      {"$match": {"quizzes._id": {"$nin": attended_quizzes}}},

      # Step 5: Project required fields
      {
          "$project": {
              "_id": 1,
              "quiz_id": "$quizzes._id",
              "quiz_title": "$quizzes.title",
              "topic_name": "$name",
              "uploaded_by": "$quizzes.uploaded_by",
              "uploaded_at": "$quizzes.uploaded_at",
              "number_of_questions": "$quizzes.number_of_questions",
              "time_limit": "$quizzes.time_limit",
              "type": "$quizzes.type",
          }
      }
  ]

  quizzes = list(topic_collection.aggregate(pipeline))
  print(quizzes)

  pipeline = [
      # Step 1: Find topics where the user is enrolled
      {"$match": {"students": user_id}},

      # Step 2: Lookup assessments that match the topic ID
      {
          "$lookup": {
              "from": "assessments",
              "localField": "_id",
              "foreignField": "topic_id",
              "as": "assessments"
          }
      },

      # Step 3: Unwind assessments to process them individually
      {"$unwind": "$assessments"},

      # Step 4: Exclude assessments the user has already completed
      # {"$match": {"assessments._id": {"$nin": completed_assessments}}},

      # Step 5: Project required fields
      {
          "$project": {
              "_id": 1,
              "assessment_id": "$assessments._id",
              "assessment_title": "$assessments.title",
              "topic_name": "$name",
              "uploaded_by": "$assessments.uploadedBy",
              "uploaded_at": "$assessments.uploaded_at",
              "description": "$assessments.description",
              "question": "$assessments.question",
          }
      }
  ]
  assessments = list(topic_collection.aggregate(pipeline))
  print(assessments)
  return render_template(
    "quiz/takeQuiz.html",
    quizzes=quizzes,
    assessments=assessments,
)

@bp.route("/quiz/intermediateQuizDetails/")
@bp.route("/quiz/intermediateQuizDetails/<id>", methods=["GET", "POST"])
@login_required
def intermediateQuizDetails(id=None):
  backPageUrl = "quiz.adminHome"
  db = get_db()
  user_collection = db["users"]
  quiz_head_collection = db["quiz_head"]
  quiz_questions_collection = db["quiz_questions"]


  quiz_head = quiz_head_collection.find_one({"_id": ObjectId(id)})
  quiz_questions = list(quiz_questions_collection.find({"quiz_head_id": ObjectId(id)}))

  uploadedBy = user_collection.find_one({"_id": quiz_head["uploaded_by"]})["username"]
  uploadedByEmail = user_collection.find_one({"_id": quiz_head["uploaded_by"]})["email"]

  subjectName = db["topic"].find_one({"_id": quiz_head["subject"]})["name"]
  return render_template(
    "quiz/intermediateQuizDetails.html",
    quiz_head=quiz_head,
    quiz_questions=quiz_questions,
    uploadedBy=uploadedBy,
    uploadedByEmail=uploadedByEmail,
    subjectName=subjectName,
  )

@bp.route("/quiz/attendQuiz/")
@bp.route("/quiz/attendQuiz/<id>", methods=["GET", "POST"])
@login_required
def attendQuiz(id=None):
  backPageUrl = "quiz.adminHome"
  db = get_db()
  user_collection = db["users"]
  quiz_head_collection = db["quiz_head"]
  quiz_questions_collection = db["quiz_questions"]
  quiz_results_collection = db["quizResults"]
  answered_questions_collection = db["answeredQuestions"]

  quiz_head = quiz_head_collection.find_one({"_id": ObjectId(id)})
  quiz_questions = list(quiz_questions_collection.find({"quiz_head_id": ObjectId(id)}))

  uploadedBy = user_collection.find_one({"_id": quiz_head["uploaded_by"]})["username"]
  uploadedByEmail = user_collection.find_one({"_id": quiz_head["uploaded_by"]})["email"]

  if request.method == "POST":
    # Get the form data
    quiz_head_id = id
    quiz_head = quiz_head_collection.find_one({"_id": ObjectId(quiz_head_id)})
    quiz_questions = list(quiz_questions_collection.find({"quiz_head_id": ObjectId(quiz_head_id)}))

    # Get the user's answers
    user_answers = {}
    for question in quiz_questions:
      question_id = str(question["_id"])
      user_answers[question_id] = request.form.get(question_id)
    print(user_answers)
    print(quiz_questions)

    # Calculate the score
    score = 0
    for question in quiz_questions:
      question_id = str(question["_id"])
      correct_option = question["correct_option"]
      if user_answers[question_id] == str(correct_option):
        print("YAY")
        score += 1
      answeredQuestionMetadata = {
        "question_id": ObjectId(question_id),
        "quiz_head_id": ObjectId(quiz_head_id),
        "question": question["question"],
        "option_1": question["option_1"],
        "option_2": question["option_2"],
        "option_3": question["option_3"],
        "option_4": question["option_4"],
        "user_answer": user_answers[question_id],
        "correct_option": correct_option,
        "is_correct": user_answers[question_id] == str(correct_option),
      }
      answered_questions_collection.insert_one(answeredQuestionMetadata)


    print(score)
    # Save the score
    db.users.update_one(
      {"_id": ObjectId(session["user_id"])},
      {"$push": {"attended_quizzes": ObjectId(quiz_head_id)}}
    )

    # Save the score in quizResults
    quiz_results_collection.insert_one({
      "quiz_head_id": ObjectId(quiz_head_id),
      "user_id": ObjectId(session["user_id"]),
      "score": score,
      "user_answers": user_answers,
      "time_taken": 0,
      "submitted_at": dt.now(),
    })

    return render_template(
      "quiz/quizResult.html",
      quiz_head=quiz_head,
      quiz_questions=quiz_questions,
      uploadedBy=uploadedBy,
      uploadedByEmail=uploadedByEmail,
      user_answers=user_answers,
      score=score,
      submitted_at=dt.now(),
    )


  return render_template(
    "quiz/attendQuiz.html",
    quiz_head=quiz_head,
    quiz_questions=quiz_questions,
    uploadedBy=uploadedBy,
    uploadedByEmail=uploadedByEmail,
  )


@bp.route("/quiz/quizResult/")
@bp.route("/quiz/quizResult/<id>")
@login_required
def quizResult(id=None):
  backPageUrl = "quiz.adminHome"
  db = get_db()
  user_collection = db["users"]
  quiz_head_collection = db["quiz_head"]
  quiz_questions_collection = db["quiz_questions"]
  quiz_results_collection = db["quizResults"]

  quiz_head_id = ObjectId(id)
  quiz_head = quiz_head_collection.find_one({"_id": ObjectId(quiz_head_id)})
  quiz_questions = list(quiz_questions_collection.find({"quiz_head_id": ObjectId(quiz_head_id)}))
  quiz_results = list(quiz_results_collection.find({"quiz_head_id": ObjectId(quiz_head_id)}))

  uploadedBy = user_collection.find_one({"_id": quiz_head["uploaded_by"]})["username"]
  uploadedByEmail = user_collection.find_one({"_id": quiz_head["uploaded_by"]})["email"]

  return render_template(
    "quiz/quizResult.html",
    quiz_head=quiz_head,
    quiz_questions=quiz_questions,
    uploadedBy=uploadedBy,
    uploadedByEmail=uploadedByEmail,
    quiz_results=quiz_results,
  )

@bp.route("/chatWithBot/")
@login_required
def chatWithBot():
  return render_template("quiz/chatWithBot.html")

@bp.route("/chat", methods=["POST"])
def chat():
  
  data = request.get_json()
  user_message = data.get("message", "")
  # Ensure a message is provided
  if not user_message:
      return jsonify({"response": "Please provide a valid message."}), 400
  try:
      # Add user message to the conversation history
      conversation_history.append(f"User: {user_message}")
      # Construct the prompt using conversation history
      history = "\n".join(conversation_history)
      prompt = (
          f"You are a helpful assistant. Use the conversation below to respond "
          f"to the user's latest query in a precise and complete manner. "
          f"Your response must be concise and between 100-150 characters:\n\n"
          f"{history}\nAI:"
      )
      # Generate a response using Llama 3.2
      raw_response = chatllm.invoke(prompt)
      bot_response = raw_response.content.strip() if hasattr(raw_response, "content") else "I couldn't generate a response."
      # Ensure response is within the character limit and well-formed
      if len(bot_response) > 150:
          # Truncate response at the last complete sentence within the limit
          truncated_response = bot_response[:150]
          if "." in truncated_response:
              bot_response = truncated_response.rsplit(".", 1)[0] + "."
          else:
              bot_response = truncated_response + "..."
      elif len(bot_response) < 100:
          # Leave short responses as they are
          bot_response = bot_response
      # Add bot response to the conversation history
      conversation_history.append(f"AI: {bot_response}")
      # Return the bot's response
      return jsonify({"response": bot_response})
  except Exception as e:
      return jsonify({"response": f"Error: {str(e)}"}), 500


@bp.route("/quiz/quizResultsWeakness/<id>", methods=["POST"])
@login_required
def quizResultsWeakness(id=None):
  return render_template("quiz/quizResultsWeakness.html")
