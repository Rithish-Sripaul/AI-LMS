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

bp = Blueprint("assessment", __name__, url_prefix="")
llm = OllamaLLM(
    model="llama3.2",
    base_url="https://4e68-115-241-193-70.ngrok-free.app",
    temperature=0,
)

@bp.route("/createAssessment", methods=["GET", "POST"])
@login_required
def createAssessment():

  db = get_db()
  document_collection = db["documents"]
  topic_collection = db["topic"]
  assessment_collection = db["assessments"]

  # Get the list of assessments made by this user
  assessments = list(assessment_collection.find({"uploadedBy": ObjectId(session["user_id"])}))

  # Get the list of existing document sort by alhapbetical order
  documents = list(document_collection.find({"uploadedBy": ObjectId(session["user_id"])}).sort({"title": 1}))
  print(documents)
  # Get the list of parent topic 
  parentTopicList = list(topic_collection.find({"isSubTopic": False}))

  # Get the list of sub parent topic
  subParentTopicList = list(topic_collection.find({"isSubTopic": True}))

  if request.method == "POST":

    title = request.form["assessment_title"]
    description = request.form["assessment_details"]
    topic_id = request.form["subject"]

    document_ids = request.form.getlist("document_id[]")
    content = []
    lesson_names = []
    for document_id in document_ids:
      document = document_collection.find_one({"_id": ObjectId(document_id)})
      content.append(document["content"])
      lesson_names.append(document["title"])
    content = " ".join(content)

    assessmentPrompt = f"""
    Generate **one** assessment question based on the given content and description.

    ### **Content:**
    "{content}"

    ### **Description:**
    "{description}"

    ### **Instructions:**
    - Use the provided **content** and **description** to create a relevant question.
    - The question should test **conceptual understanding**, **analysis**, or **application**.
    - Avoid direct recall-based questions.
    - Ensure clarity and precision in wording.
    - The question should have well written examples that further explain the concept.
    - The question should also have optional restrictions that make the question more challenging.

    Provide the output strictly in JSON format with the following structure:

    {{
        "question": "<Generated Assessment Question>"
    }}

    Ensure the question is well-structured and aligned with the given content.
    Output only the JSON.
    """
    json_response = llm.invoke(assessmentPrompt)
    assessmentJSON = json.loads(json_response)
    print(assessmentJSON)
    assessmentJSON["uploadedBy"] = ObjectId(session["user_id"])
    assessmentJSON["uploaded_at"] = dt.now()
    assessmentJSON["documents"] = document_ids
    assessmentJSON["lesson_names"] = lesson_names
    assessmentJSON["topic_id"] = ObjectId(topic_id)
    assessmentJSON["title"] = title
    assessmentJSON["description"] = description
    assessment_collection.insert_one(assessmentJSON)

    return redirect(url_for("assessment.createAssessment"))


  return render_template(
    "assessment/createAssessment.html",
    documentsList=documents,
    parentTopicList=parentTopicList,
    subParentTopicList=subParentTopicList,
    assessments=assessments
  )

@bp.route("assessmentDetails/<id>", methods=["GET", "POST"])
@login_required
def assessmentDetails(id):
  db = get_db()
  assessment_collection = db["assessments"]
  document_collection = db["documents"]
  topic_collection = db["topic"]

  # subject = topic_collection.find_one({"_id": ObjectId(id)})["name"]
  # topic = topic_collection.find_one({"_id": assessment["topic_id"]})

  assessment = assessment_collection.find_one({"_id": ObjectId(id)})
  documents = []
  for document_id in assessment["documents"]:
    document = document_collection.find_one({"_id": ObjectId(document_id)})
    documents.append(document)

  # if request.method == "POST":
    

  return render_template(
    "assessment/assessmentDetails.html",
    assessment=assessment,
    documents=documents,
    # topic=topic,
    # subject=subject
  )