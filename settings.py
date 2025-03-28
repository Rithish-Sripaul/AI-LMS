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

bp = Blueprint("settings", __name__, url_prefix="")

@bp.route("/settings/topic/", methods=["GET", "POST"])
@login_required
def topic():
  backPageUrl = "documents.search"

  # Toast Message
  try:
    if session["toastMessage"] != "":
      flash(session["toastMessage"], session["toastMessageCategory"])
      print("Toast Message sent")
      session["toastMessage"] = ""
  except:
    pass

  db = get_db()
  topic_collection = db["topic"]

  # Get the list of existing parent topics
  topicsList = list(
    topic_collection.find({"isSubTopic": False})
  ) 

  # Get the list of existing topics
  topicsListLen = topic_collection.count_documents({})

  # Setting up pagination details
  list_number_of_documents_per_page = [5, 10, 20, 40]
  if request.args.get("docppag") is not None:
    session["number_of_documents_per_page"] = request.args.get("docppag", type=int)
  number_of_documents_per_page = session["number_of_documents_per_page"]

  current_page = request.args.get('page', default=0, type=int)
  number_of_pages = math.ceil(topicsListLen / number_of_documents_per_page)


  topicsList = list(
      topic_collection.aggregate([
          {
              "$lookup": {
                  "from": "topic",
                  "localField": "parentTopic",
                  "foreignField": "_id",
                  "as": "parentTopicDetails"
              }
          },
          {
              "$addFields": {
                  "parentTopicName": {
                    "$arrayElemAt": ["$parentTopicDetails.name", 0]
                  }
              }
          },
          {
              "$project": {
                  "parentTopicDetails": 0
              }
          },
          { "$sort": {"uploadedAt": -1} },
          { "$skip": number_of_documents_per_page * current_page },
          { "$limit": number_of_documents_per_page },

      ])
    )

  if request.method == "POST":
    # NEW TOPIC
    if "topic-submit" in request.form:
      topicName = request.form["topic_name"]

      documentExists = topic_collection.find_one({"name": topicName})
      if documentExists:
        session["toastMessage"] = "Topic already exists"
        session["toastMessageCategory"] = "Alert"
        return redirect(url_for("settings.topic"))

      document_metadata = {
        "name": topicName,
        "uploaded_by": ObjectId(session["user_id"]),
        "hasSubTopic": False,
        "isSubTopic": False,
        "parentTopic": None,
        "documentCount": 0,
        "uploadedAt": datetime.datetime.now(),
      }

      try:
        topic_collection.insert_one(document_metadata)
        session["toastMessage"] = "Topic uploaded successfully"
        session["toastMessageCategory"] = "Success"
        return redirect(url_for("settings.topic"))
      except:
        print("Couldn't upload topic")
    
    # NEW SUB TOPIC
    elif "sub-topic-submit" in request.form:
      parentTopic = request.form["parent_topic"]
      subTopicName = request.form["sub_topic"]

      documentExists = topic_collection.find_one(
        {
          "name": subTopicName,
          "parentTopic": ObjectId(parentTopic)
        })
      if documentExists:
        session["toastMessage"] = "Sub Topic already exists"
        session["toastMessageCategory"] = "Alert"
        return redirect(url_for("settings.topic"))

      document_metadata = {
        "name": subTopicName,
        "uploaded_by": ObjectId(session["user_id"]),
        "hasSubTopic": False,
        "isSubTopic": True,
        "parentTopic": ObjectId(parentTopic),
        "documentCount": 0,
        "uploadedAt": datetime.datetime.now(),
      }

      # Upload sub topic and update parent topic
      try:
        topic_collection.insert_one(document_metadata)
        topic_collection.update_one(
          { "_id": ObjectId(parentTopic) },
          {
            "$set": {
              "hasSubTopic": True
            }
          }
        )
        session["toastMessage"] = "Sub Topic uploaded successfully"
        session["toastMessageCategory"] = "Success"
        return redirect(url_for("settings.topic"))
      except:
        print("Couldn't upload sub topic")
  
  return render_template(
    "settings/topic.html",
    backPageUrl = backPageUrl,
    topicsList = topicsList,
    topicsListLen = len(topicsList),
    number_of_pages = number_of_pages,
    list_number_of_documents_per_page = list_number_of_documents_per_page,
    number_of_documents_per_page = number_of_documents_per_page,
    current_page = current_page,
  )


  backPageUrl = "documents.search"

  # Toast Message
  try:
    if session["toastMessage"] != "":
      flash(session["toastMessage"], session["toastMessageCategory"])
      print("Toast Message sent")
      session["toastMessage"] = ""
  except:
    pass

  db = get_db()
  report_collection = db["reportType"]
  divisions_collection = db["divisions"]
 
  # Get the list of existing Parent report types
  parentReportTypeList = list(
    report_collection.find({"isSubReportType": False})
  )

  # Get the list of existing report types
  reportTypesListLen = report_collection.count_documents({})

  # Setting up pagination details
  list_number_of_documents_per_page = [5, 10, 20, 40]
  if request.args.get("docppag") is not None:
    session["number_of_documents_per_page"] = request.args.get("docppag", type=int)
  number_of_documents_per_page = session["number_of_documents_per_page"]

  current_page = request.args.get('page', default=0, type=int)
  number_of_pages = math.ceil(reportTypesListLen / number_of_documents_per_page)

  reportTypesList = list(
      report_collection.aggregate([
          {
              "$lookup": {
                  "from": "reportType",
                  "localField": "parentReportType",
                  "foreignField": "_id",
                  "as": "parentReportTypeDetails"
              }
          },
          {
              "$addFields": {
                  "parentReportTypeName": {
                    "$arrayElemAt": ["$parentReportTypeDetails.name", 0]
                  }
              }
          },
          {
              "$project": {
                  "parentReportTypeDetails": 0
              }
          },
          { "$sort": {"uploadedAt": -1} },
          { "$skip": number_of_documents_per_page * current_page },
          { "$limit": number_of_documents_per_page },

      ])
    )
  if request.method == "POST":
    # NEW REPORT TYPE
    if "report-type-submit" in request.form:
      reportTypeName = request.form["report_type_name"]

      documentExists = report_collection.find_one({"name": reportTypeName})
      if documentExists:
        session["toastMessage"] = "Report Type already exists"
        session["toastMessageCategory"] = "Alert"
        return redirect(url_for("settings.reportType"))


      document_metadata = {
        "name": reportTypeName,
        "uploaded_by": ObjectId(session["user_id"]),
        "hasSubReportType": False,
        "isSubReportType": False,
        "parentReportType": None,
        "documentCount": 0,
        "uploadedAt": datetime.datetime.now(),
      }

      try:
        report_collection.insert_one(document_metadata)
        session["toastMessage"] = "Report Type uploaded successfully"
        session["toastMessageCategory"] = "Success"
        return redirect(url_for("settings.reportType"))
      except:
        print("Couldn't upload report type")
    
    # NEW SUB REPORT TYPE
    elif "sub-report-type-submit" in request.form:
      parentReportType = request.form["parent_report_type"]
      subReportTypeName = request.form["sub_report_type"]
      print(parentReportType)

      documentExists = report_collection.find_one(
        {
          "name": subReportTypeName,
          "parentReportType": ObjectId(parentReportType)
        })
      if documentExists:
        session["toastMessage"] = "Sub Report Type already exists"
        session["toastMessageCategory"] = "Alert"
        return redirect(url_for("settings.reportType"))
      document_metadata = {
        "name": subReportTypeName,
        "uploaded_by": ObjectId(session["user_id"]),
        "hasSubReportType": False,
        "isSubReportType": True,
        "parentReportType": ObjectId(parentReportType),
        "documentCount": 0,
        "uploadedAt": datetime.datetime.now(),
      }

      # Upload sub report type and update parent report type
      try:
        report_collection.insert_one(document_metadata)
        report_collection.update_one(
          { "_id": ObjectId(parentReportType) },
          {
            "$set": {
              "hasSubReportType": True
            }
          }
        )
        session["toastMessage"] = "Sub Report Type uploaded successfully"
        session["toastMessageCategory"] = "Success"
        return redirect(url_for("settings.reportType"))
      except:
        print("Couldn't upload sub report type")

  return render_template(
    "settings/reportType.html",
    backPageUrl = backPageUrl,
    reportTypesList = reportTypesList,
    reportTypesListLen = len(reportTypesList),
    parentReportTypeList = parentReportTypeList,
    number_of_pages = number_of_pages,
    list_number_of_documents_per_page = list_number_of_documents_per_page,
    number_of_documents_per_page = number_of_documents_per_page,
    current_page = current_page,
  )