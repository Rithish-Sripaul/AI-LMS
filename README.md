# AI-Powered Learning management System

## Overview
This is an AI-powered learning management system that enables professors to assign student to their classes, OCR-based PDF processing, and automated assessment generation from uploaded PDFs. It integrates Flask, MongoDB, and various AI tools for intelligent document analysis and retrieval.

## Features
- **Classes and Students:** Professors can create a number of classes and assign students to them.
- **Learning Content:** Professors can upload PDFs as learning content.
- **AI-Powered Summarization:** Automatically generate summaries and abstracts for PDFs. Allows students to glance through the PDF at ease.
- **OCR Integration:** Extract text from scanned documents.
- **Assessment Generation:** Create quizzes based on document content and assign them to Students.
- **View quiz results:** Professors can then view the results of the quizzes attended by students.
- **Automated Remarks on quiz results:** An AI powered agent will generate the strong point and the weak points of the Student based on the quiz, this qill be extremely helpful for the student for futher revision.

## Tech Stack
- **Backend:** Python, Flask
- **Database:** MongoDB
- **Frontend:** Jinja2 (Templating), HTML, CSS, Bootstrap, JavaScript
- **AI & NLP:** OCR, Llama-based NLP Models

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.10+
- MongoDB
- Tesseract OCR
- Docker (optional for containerized deployment)

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the flask application:
   ```bash
   flask --app app run
   ```
4. Run local MongoDB
    ```bash
   mongosh
   ```
6. Access the application at `http://localhost:5000`.


## License
MIT License

