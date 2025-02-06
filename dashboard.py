import os
import datetime
import math
from flask import render_template, redirect, request, url_for, Blueprint, flash, session, make_response
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from authentication import login_required
import pymongo
from database import get_db
from bson.objectid import ObjectId

bp = Blueprint("dashboard", __name__, url_prefix="")

@bp.route("/home")
@login_required
def home():
  backPageUrl = "dashboard.home"
  isAdmin = session["isAdmin"]

 
  try:
    if session["toastMessage"] != "":
      flash(session["toastMessage"], "Success")
      print("Toast Message sent")
      session["toastMessage"] = ""
  except:
    pass

  db = get_db()
  document_collection = db["documents"]
  user_collection = db["users"]
  searchHistory_collection = db["searchHistory"]
  quiz_head_collection = db["quiz_head"]
  topic_collection = db["topic"]
  divisions_collection = db["divisions"]
  numberOfStudent = 0

  # Getting the number of students that have the current user under theit teachers list
  numberOfStudent = user_collection.count_documents({"teachers": ObjectId(session["user_id"])})
  print(numberOfStudent)


  # Number of quiz created by the user
  numberOfQuiz = quiz_head_collection.count_documents({"uploaded_by": ObjectId(session["user_id"])})

  # NUmber of topics created by the user
  numberOfTopics = 0
  numberOfTopics = topic_collection.count_documents({"uploaded_by": ObjectId(session["user_id"])})


  # SEARCH HISTORY
  searchHistory = list(
    searchHistory_collection
    .aggregate([
      {
        "$match": { "user_id": ObjectId(session["user_id"]) }
      },
      {
        "$lookup": {
          "from": "documents",
          "localField": "document_id",
          "foreignField": "_id",
          "as": "document_details"
        }
      },
      {
        "$unwind": "$document_details"
      },
      {
        "$project": {
          "document_id": 1,
          "document_details.title": 1,
          "document_details.document_number": 1,
          "document_details.year": 1,
          "document_details.author": 1,
          "document_details.division": 1,
          "document_details.reportType": 1,
          "document_details.uploaded_at": 1,
          "timestamp": 1
        }
      },
      {
        "$sort": {
          "timestamp": -1
        }
      },
      {
        "$limit": 5
      }
    ])
  )

  # PAST UPLOADS
  pastUploads_limit = 5 # No. of documents to show
  pastUploads = list(
    document_collection
    .find({"uploadedBy" : ObjectId(session["user_id"])})
    .sort({"uploaded_at": -1})
    .limit(pastUploads_limit)
  )

  # DIVISION ANALYTICS
  division_wind_tunnel = divisions_collection.find_one(
      {
        "name": "Wind Tunnel"
      }
  )

  division_hstt = divisions_collection.find_one(
    {
      "name": "HSTT"
    }
  )

  division_smb = divisions_collection.find_one(
    {
      "name": "SMB"
    }
  )

  division_ct = divisions_collection.find_one(
    {
      "name": "CT"
    }
  )

  division_cfd = divisions_collection.find_one(
    {
      "name": "CFD"
    }
  )


  # LATEST GLOBAL UPLOADS
  latestGlobalUploads = list(
    document_collection
    .find({})
    .sort({"uploaded_at": -1})
    .limit(5)
  )


  return render_template(
    "home/dashboard.html",
    backPageUrl = backPageUrl,
    isAdmin = isAdmin,
    searchHistory = searchHistory,
    pastUploads = pastUploads,
    division_wind_tunnel = division_wind_tunnel,
    division_hstt = division_hstt,
    division_smb = division_smb,
    division_ct = division_ct,
    division_cfd = division_cfd,
    latestGlobalUploads = latestGlobalUploads,
    numberOfStudent = numberOfStudent,
    numberOfQuiz = numberOfQuiz,
    numberOfTopics = numberOfTopics
  )

@bp.route("/homeStudent")
@login_required
def homeStudent():
  backPageUrl = "dashboard.home"
  isAdmin = session["isAdmin"]

 
  try:
    if session["toastMessage"] != "":
      flash(session["toastMessage"], "Success")
      print("Toast Message sent")
      session["toastMessage"] = ""
  except:
    pass

  db = get_db()
  document_collection = db["documents"]
  user_collection = db["users"]
  searchHistory_collection = db["searchHistory"]
  quiz_head_collection = db["quiz_head"]
  topic_collection = db["topic"]
  divisions_collection = db["divisions"]
  numberOfStudent = 0

  # Number of quized the user has taken
  numberOfQuiz = len(user_collection.find_one({"_id": ObjectId(session["user_id"])})["attended_quizzes"])
  print(numberOfQuiz)

  # Number of topics the user is under
  numberOfTopics = topic_collection.count_documents({"students": ObjectId(session["user_id"])})

  # SEARCH HISTORY
  searchHistory = list(
    searchHistory_collection
    .aggregate([
      {
        "$match": { "user_id": ObjectId(session["user_id"]) }
      },
      {
        "$lookup": {
          "from": "documents",
          "localField": "document_id",
          "foreignField": "_id",
          "as": "document_details"
        }
      },
      {
        "$unwind": "$document_details"
      },
      {
        "$project": {
          "document_id": 1,
          "document_details.title": 1,
          "document_details.document_number": 1,
          "document_details.year": 1,
          "document_details.author": 1,
          "document_details.division": 1,
          "document_details.reportType": 1,
          "document_details.uploaded_at": 1,
          "timestamp": 1
        }
      },
      {
        "$sort": {
          "timestamp": -1
        }
      },
      {
        "$limit": 5
      }
    ])
  )

  # PAST UPLOADS
  pastUploads_limit = 5 # No. of documents to show
  pastUploads = list(
    document_collection
    .find({"uploadedBy" : ObjectId(session["user_id"])})
    .sort({"uploaded_at": -1})
    .limit(pastUploads_limit)
  )

  # DIVISION ANALYTICS
  division_wind_tunnel = divisions_collection.find_one(
      {
        "name": "Wind Tunnel"
      }
  )

  division_hstt = divisions_collection.find_one(
    {
      "name": "HSTT"
    }
  )

  division_smb = divisions_collection.find_one(
    {
      "name": "SMB"
    }
  )

  division_ct = divisions_collection.find_one(
    {
      "name": "CT"
    }
  )

  division_cfd = divisions_collection.find_one(
    {
      "name": "CFD"
    }
  )


  # LATEST GLOBAL UPLOADS
  latestGlobalUploads = list(
    document_collection
    .find({})
    .sort({"uploaded_at": -1})
    .limit(5)
  )

  # Get the id and name of quizzes attended by the uesr
  attendedQuizzes = user_collection.find_one({"_id": ObjectId(session["user_id"])})["attended_quizzes"]
  attendedQuizzesDetails = []
  for quiz in attendedQuizzes:
    quizDetails = quiz_head_collection.find_one({"_id": ObjectId(quiz)})
    attendedQuizzesDetails.append(quizDetails)


  return render_template(
    "quiz/analysisStudent.html",
    backPageUrl = backPageUrl,
    isAdmin = isAdmin,
    searchHistory = searchHistory,
    pastUploads = pastUploads,
    division_wind_tunnel = division_wind_tunnel,
    division_hstt = division_hstt,
    division_smb = division_smb,
    division_ct = division_ct,
    division_cfd = division_cfd,
    latestGlobalUploads = latestGlobalUploads,
    numberOfTopics = numberOfTopics,
    numberOfQuiz = numberOfQuiz,
    attendedQuizzesDetails = attendedQuizzesDetails
  )
