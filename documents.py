# ----------------- IMPORTS -----------------

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
bp = Blueprint("documents", __name__, url_prefix='')

# ----------------- SEARCH -----------------

@bp.route("/search/", methods=["GET", "POST"])
@login_required
def search():
    backPageUrl = "dashboard.home"

    db = get_db()
    user_collection = db["users"]
    document_collection = db["documents"]

    searchResults = list(document_collection.find())


    # # userDivision = user_collection.find_one({"_id": ObjectId(session["user_id"])})["division"]

    # # Toast
    # try:
    #     if session["toastMessage"] != "":
    #         flash(session["toastMessage"], session["toastMessageCategory"])
    #         print("Toast Message sent")
    #         session["toastMessage"] = ""
    #         session["toastMessageCategory"] = ""
    # except:
    #     pass

    # # Report types
    # report_type_collection = db["reportType"]
    # reportTypeList = list(report_type_collection.find())

    # # Parent Report Types
    # parentReportTypeList = list(
    #     report_type_collection.find(
    #         {
    #             "isSubReportType": False
    #         }
    #     )
    # )

    # # Division types
    # divisions_collection = db["divisions"]
    # divisionList = list(divisions_collection.find())
    
    # list_number_of_documents_per_page = [5, 10, 20, 40]
    # number_of_pages = 1
    # number_of_documents_per_page = 5
    # current_page = 0

    # yearList = document_collection.distinct("year")

    # # CONSTRUCTING THE METADATA
    # searchMetaData = {}

    # refreshDocumentTitle = ""
    # refreshDocumentNumber = ""
    # refreshAuthorName = ""
    # refreshDocumentYear = ""
    # refreshDivision = ""
    # refreshReportType = ""
    # refreshSubReportType = ""
    
    # # document_title
    # if request.args.get("document_title", default = "") != "":
    #     searchMetaData["$text"] = {"$search": request.args.get("document_title", default="")}
    #     refreshDocumentTitle = request.args.get("document_title")
    # else:
    #     searchMetaData.pop("$text", None)
    # # document_number
    # if request.args.get("document_number", default = "") != "":
    #     searchMetaData["document_number"] = {"$regex": request.args.get("document_number"), "$options": "i"}    
    #     refreshDocumentNumber = request.args.get("document_number")
    # else:
    #     searchMetaData.pop("document_number", None)
    # # author_name
    # if request.args.get("author", default = "") != "":
    #     searchMetaData["author_list"] = request.args.get("author")
    #     searchMetaData["author_list"] = {"$regex": request.args.get("author"), "$options": "i"}
    #     refreshAuthorName = request.args.get("author")
    # else:
    #     searchMetaData.pop("author", None)
    # # document_year
    # if request.args.get("year", default = "") != "":
    #     searchMetaData["year"] = int(request.args.get("year"))
    #     refreshDocumentYear = request.args.get("year")
    # else:
    #     searchMetaData.pop("year", None)
    # # division
    # if request.args.get("division", default = "") != "":
    #     searchMetaData["division"] = request.args.get("division")
    #     refreshDivision = request.args.get("division")
    # else:
    #     searchMetaData.pop("division", None)
    # # report type
    # if request.args.get("reportType", default = "") != "":
    #     searchMetaData["reportType"] = report_type_collection.find_one({"_id": ObjectId(request.args.get("reportType"))})["name"]
    #     refreshReportType = report_type_collection.find_one({"_id": ObjectId(request.args.get("reportType"))})["name"]
    # else:
    #     searchMetaData.pop("reportType", None)
    # # sub report type
    # if request.args.get("subReportType", default = "") != "":
    #     searchMetaData["subReportType"] = report_type_collection.find_one({"_id": ObjectId(request.args.get("subReportType"))})["name"]
    #     refreshSubReportType = report_type_collection.find_one({"_id": ObjectId(request.args.get("subReportType"))})["name"]
    # else:
    #     searchMetaData.pop("subReportType", None)
    
    # # CONSTRUCTING SORTING META DATA
    # sortMetaData = {}
    # refreshSortData = {}

    # if request.args.get("sortBy", default="") == "uploaded_at_asc":
    #     sortMetaData["uploaded_at"] = 1
    # elif request.args.get("sortBy", default="") == "uploaded_at_desc":
    #     sortMetaData["uploaded_at"] = -1
    # elif request.args.get("sortBy", default="") == "title_asc":
    #     sortMetaData["title"] = 1
    # elif request.args.get("sortBy", default="") == "title_desc":
    #     sortMetaData["title"] = -1
    # elif request.args.get("sortBy", default="") == "author_asc":
    #     sortMetaData["author"] = 1
    # elif request.args.get("sortBy", default="") == "author_desc":
    #     sortMetaData["author"] = -1
    # elif request.args.get("sortBy", default="") == "year_asc":
    #     sortMetaData["year"] = 1
    # elif request.args.get("sortBy", default="") == "year_desc":
    #     sortMetaData["year"] = -1
    
    # if sortMetaData == {}:
    #     sortMetaData["uploaded_at"] = -1

    # print(sortMetaData)
    # print(refreshSortData)
    # print(searchMetaData)
    # print(refreshReportType)
    # # OPEN/CLOSE the SORT COLLAPSIBLE
    # sortCollapse = ""
    # if refreshSortData == {}:
    #     sortCollapse = ""
    # else:
    #     sortCollapse = "show"
    # print(sortCollapse)
    # # DEFAULT VIEW: Recently uploaded documents
    # search_results = list(document_collection.find(searchMetaData))

    # totalNumberOfDocuments = len(search_results)
    
    # # Setting up pagination details
    # if request.args.get("docppag") is not None:
    #     session["number_of_documents_per_page"] = request.args.get("docppag", type=int)
    # number_of_documents_per_page = session["number_of_documents_per_page"]
    # current_page = request.args.get('page', default=0, type=int)
    # number_of_pages = math.ceil(totalNumberOfDocuments / number_of_documents_per_page)

    # searchResultsTrimmed = list(document_collection.find(
    #     searchMetaData,
    #     skip = number_of_documents_per_page * current_page,
    #     limit = number_of_documents_per_page,
    #     sort = sortMetaData
    # ))


    return render_template(
        "search/retreiveDocuments.html",
        backPageUrl = backPageUrl,
        searchResults = searchResults,
        # userDivision = userDivision,
        # yearList = sorted(yearList),
        # searchResults = searchResultsTrimmed, 
        # lenSearchResults = searchResultsTrimmedLen,
        # reportTypeList = reportTypeList,
        # parentReportTypeList = parentReportTypeList,
        # divisionList = divisionList,
        # number_of_pages = number_of_pages,
        # list_number_of_documents_per_page = list_number_of_documents_per_page,
        # number_of_documents_per_page = number_of_documents_per_page,
        # current_page = current_page,
        # refreshDocumentTitle = refreshDocumentTitle,
        # refreshDocumentNumber = refreshDocumentNumber,
        # refreshAuthorName = refreshAuthorName,
        # refreshDocumentYear = refreshDocumentYear,
        # refreshDivision = refreshDivision,
        # refreshReportType = refreshReportType,
        # refreshSubReportType = refreshSubReportType,
        # refreshSortDocumentTitle = refreshSortData.get("document_title", ""),
        # refreshSortAuthor = refreshSortData.get("author", ""),
        # refreshSortYear = refreshSortData.get("year", ""),
        # refreshSortDivision = refreshSortData.get("division", ""),
        # refreshSortUploadedAt = refreshSortData.get("uploaded_at", ""),
        # sortCollapse = sortCollapse
    )


# ----------------- UPLOAD -----------------

@bp.route("/upload/", methods=["GET", "POST"])
@login_required
def upload():

    llm = OllamaLLM(
        model="llama3.2",
        base_url="https://4e68-115-241-193-70.ngrok-free.app",
        temperature=0,
    )

    backPageUrl = "documents.search"

    # Toast Message
    try:
        if session["toastMessage"] != "":
            flash(session["toastMessage"], session["toastMessageCategory"])
            print("Toast Message sent")
            session["toastMessage"] = ""
            session["toastMessageCategory"] = ""
    except:
        pass

    db = get_db()
    document_collection = db["documents"]
    user_collection = db["users"]
    file_collection = db["fs.files"]
    topic_collection = db["topic"]

    # Parent Topic List
    parentTopicList = list(
        topic_collection.find(
            {
                "isSubTopic": False
            }
        )
    )
    parentTopicListLen = len(parentTopicList)

    # Sub Topic List
    subTopicList = list(
        topic_collection.find(
            {
                "isSubTopic": True
            }
        )
    )

    totalNumberOfDocuments = document_collection.count_documents({
        "uploadedBy" : ObjectId(session["user_id"])
    })

    # Setting up Pagination Details
    list_number_of_documents_per_page = [5, 10, 20, 40]
    if request.args.get('docppag') is not None:
        session["number_of_documents_per_page"] = request.args.get("docppag", type=int)
    number_of_documents_per_page = session["number_of_documents_per_page"]

    current_page = request.args.get('page', default=0, type=int)
    number_of_pages = math.ceil(totalNumberOfDocuments / number_of_documents_per_page)

    uploadedDocuments = list(
        document_collection
        .find({"uploadedBy" : ObjectId(session["user_id"])})
        .sort({"uploaded_at": -1})
        .skip(number_of_documents_per_page * current_page)
        .limit(number_of_documents_per_page)
    )

    if request.method == "POST":
        db = get_db()
        document_collection = db["documents"]
        fs = gridfs.GridFS(db)

        title = request.form["document_title"]
        
        topicId = ObjectId(request.form["topic"])
        if request.form.get("sub_topic", False) != False:
            subTopicId = ObjectId(request.form["sub_topic"])
        else:
            subTopicId = None
        
        file_data = request.files["documents"]
        ocrValue = request.form.getlist("ocrValue")

        topic = topic_collection.find_one({"_id": topicId})["name"]
        if subTopicId != None:
            subTopic = topic_collection.find_one({"_id": subTopicId})["name"]
        else:
            subTopic = None

        checkFileExists = list(file_collection.find({"filename": file_data.filename}))
        print(checkFileExists)
        checkFileExists = True if len(checkFileExists) != 0 else False
        print(checkFileExists)

        if False:
            # flash("File already exists. Please choose another file.", "Alert")
            session["toastMessage"] = "File already exists. Please choose another file."
            session["toastMessageCategory"] = "Alert"
            return redirect(url_for("documents.upload"))
        else:
            content = []
            if "true" in ocrValue:
                file_data.save(os.path.join("converted_pdf/", "input_pdf_test.pdf"))
                ocrmypdf.ocr("converted_pdf/input_pdf_test.pdf", "converted_pdf/ouptut_pdf.pdf", deskew=True, force_ocr=True,output_type="pdf" )
                converted_file_data = open("converted_pdf/ouptut_pdf.pdf", 'rb')
                file_id = fs.put(converted_file_data, filename=file_data.filename)
                reader = PdfReader(converted_file_data)
            else:
                file_id = fs.put(file_data, filename=file_data.filename)
                reader = PdfReader(file_data)

            for page in reader.pages:
                content.append(page.extract_text())
            content = str(content)
            content = content.replace("\\n", " ")

            # SUMMARY CREATION with HTML conversion
            prompt = f"""
            You are an intelligent assistant designed to help students understand complex topics. Your goal is to read and restructure the contents of a given PDF in a way that makes learning easier.

            Task:
            	•	Summarize and explain the concepts clearly.
            	•	Use simple language and avoid unnecessary complexity.
            	•	Organize content with proper headings and subheadings.
            	•	Include meaningful examples with explanations.
            	•	State the reasoning behind each example to improve comprehension.
            
            Output Format:
            Ensure the explanation is well-structured with:
            	1.	Headings & Subheadings
            	2.	Concise explanations
            	3.	Relevant examples with explanations
            
            Your goal is to make learning engaging, structured, and easy to understand for students.

            Here is the content:
            {content}
            """
            summary = llm.invoke(prompt)
            promptHTML = f"""
            You are an AI that converts textual content into structured HTML format. 
            Ensure proper usage of <h5>, <h6>, <p>, <ul>/<li>, <b> and <i> tags where appropriate.

            Convert the following text into valid HTML:

            {summary}
            """
            summaryHTML = llm.invoke(promptHTML)

            # EXAMPLE CREATION with HTML conversion
            examplePrompt = f"""
            You are an AI that generates clear and relevant examples based on the provided content.

            ### **Instructions:**
            - Ensure examples are **directly related** to the content.
            - Make them **easy to understand** and **practical**.
            - If the content is **technical or coding-related**, generate **code-based examples**.
            - If the content is **theoretical**, provide **real-world applications**.
            - If the content **already contains examples**, make sure to **include all of them** in your response.
            - Additionally, generate **new examples** to further illustrate the concept.
            - Keep the explanations **concise and meaningful**.

            ### **Content:**
            {content}

            ### **Generate relevant examples:**
            """

            examples = llm.invoke(examplePrompt)
            examplesPromptHTML = f"""
            You are an AI that converts textual content into structured HTML format.
            Ensure proper usage of <h5>, <h6>, <p>, <ul>/<li>, <b> and <i> tags where appropriate.
            These are examples, if they are code, ensure that they are properly formatted. with appropriate amounts of tab spaces and line breaks.

            Convert the following text into valid HTML:

            {examples}
            """
            examplesHTML = llm.invoke(examplesPromptHTML)

            
            document_metadata = {
                "uploadedBy": ObjectId(session["user_id"]),
                "title": title,
                "topic": topic,
                "subTopic": subTopic,
                "file_id": file_id,
                "isApproved": 0,
                "approvedBy": None,
                "approved_at": None,
                "content": str(content),
                "uploaded_at": datetime.datetime.now(),
                "summary": summary,
                "summaryHTML": summaryHTML,
                "examples": examples,
                "examplesHTML": examplesHTML,
            }

            try:
                document_collection.insert_one(document_metadata)
                topic_collection.update_one(
                    {
                        "name": str(topic)
                    },
                    {
                        "$inc": {
                            "documentCount": 1
                        }
                    }
                )
                if subTopic != None:
                    topic_collection.update_one(
                        {
                            "name": str(subTopic)
                        },
                        {
                            "$inc": {
                                "documentCount": 1
                            }
                        }
                    )
                print("Successfully uploaded the document")
                session["toastMessage"] = "Document uploaded successfully"
                session["toastMessageCategory"] = "Success"
            except:
                print("some error")

            return redirect(url_for("documents.upload"))

    return render_template(
        "search/uploadDocuments.html",
        backPageUrl = backPageUrl,
        uploadedDocuments = uploadedDocuments,
        uploadedDocumentsLen = len(uploadedDocuments),
        totalNumberOfDocuments = totalNumberOfDocuments,
        number_of_pages = number_of_pages,
        list_number_of_documents_per_page = list_number_of_documents_per_page,
        number_of_documents_per_page = number_of_documents_per_page,
        current_page = current_page,
        parentTopicList = parentTopicList,
        subTopicList = subTopicList,
    )

# ----------------- Backend Function for getting Report Types in JS -----------------
@bp.route("/upload/getReportTypes")
@login_required
def getReportTypes():
    db = get_db()
    report_type_collection = db["topic"]
    reportTypeList = list(report_type_collection.find())
    
    return Response(json_util.dumps(reportTypeList), mimetype="application/json")


# ----------------- DETAILS -----------------
@bp.route("/details/")
@bp.route("/details/<id>")
@login_required
def details(id=None):
    backPageUrl = "documents.search"
    db = get_db()
    user_collection = db["users"]
    document_collection = db["documents"]

    searchResults = document_collection.find_one({"_id": ObjectId(id)})
    uploadedBy = user_collection.find_one({"_id": searchResults["uploadedBy"]})["username"]
    uploadeByEmail = user_collection.find_one({"_id": searchResults["uploadedBy"]})["email"]
    # Toast
    try:
        if session["toastMessage"] != "":
            flash(session["toastMessage"], session["toastMessageCategory"])
            print("Toast Message sent")
            session["toastMessage"] = ""
            session["toastMessageCategory"] = ""
    except:
        pass
    
    return render_template(
        "search/documentDetails.html", 
        backPageUrl = backPageUrl,
        searchResults = searchResults,
        isAdmin = session["isAdmin"],
        uploadedBy = uploadedBy,
        uploadedByEmail = uploadeByEmail
    )


# ----------------- DOWNLOAD DOCUMENT -----------------
@bp.route("/download/<id>")
@login_required
def download(id = None):
    db = get_db()
    grid_fs = GridFS(db)
    file_data = grid_fs.find_one({'_id': ObjectId(id)})
    # Read the file content
    file_stream = io.BytesIO(file_data.read())
    # Send the file as a response
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=file_data.filename,
        mimetype=file_data.content_type
    )


# ----------------- SEARCH HISTORY -----------------
@bp.route("/search/searchHistory/")
@login_required
def searchHistory():
    backPageUrl = "documents.search"
    db = get_db()
    searchHistory_collection = db["searchHistory"]
    document_collection = db["documents"]
    user_collection = db["users"]
    
    # Search History of Current User
    searchHistoryList = list(
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
        { "$sort": { "timestamp": -1 } },
        ])
    )
    searchHistoryListLen = len(searchHistoryList)

    # Setting up pagination details
    list_number_of_documents_per_page = [5, 10, 20, 40, 60, 80]
    if request.args.get("docppag") is not None:
        session["number_of_documents_per_page"] = request.args.get("docppag", type=int)
    number_of_documents_per_page = session["number_of_documents_per_page"]
    current_page = request.args.get('page', default=0, type=int)
    number_of_pages = math.ceil(searchHistoryListLen / number_of_documents_per_page)

    searchHistoryList = list(
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
        { "$sort": { "timestamp": -1 } },
        { "$skip": number_of_documents_per_page * current_page },
        { "$limit": number_of_documents_per_page },
        ])
    )
    searchHistoryListLen = len(searchHistoryList)

    return render_template(
        "search/searchHistory.html",
        backPageUrl = backPageUrl,
        searchHistoryList = searchHistoryList,
        searchHistoryListLen = searchHistoryListLen,
        number_of_pages = number_of_pages,
        list_number_of_documents_per_page = list_number_of_documents_per_page,
        number_of_documents_per_page = number_of_documents_per_page,
        current_page = current_page
    )

