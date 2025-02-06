import os   
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask import render_template, send_file, redirect, request, url_for, Blueprint, flash, session, make_response
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from flask_cors import CORS
from langchain_ollama.chat_models import ChatOllama


app = Flask(__name__)
CORS(app)
# app.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

app.config["MONGO_URI"] = "mongodb://mongo:27017/dev"
app.config.from_mapping(SECRET_KEY="dev")

ollama_base_url = "https://4e68-115-241-193-70.ngrok-free.app"  # Replace <REMOTE_SERVER_URL> with your server's base URL
llm = ChatOllama(model="llama3.2", base_url=ollama_base_url)

conversation_history = []  # List to store user and bot messages

@app.route("/")
def index():
    return redirect(url_for("authentication.login"))

def register_blueprints(app):
    import authentication
    import documents
    import documentApproval
    import settings
    import dashboard
    import quiz
    import assessment
    app.register_blueprint(authentication.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(documentApproval.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(quiz.bp)
    app.register_blueprint(assessment.bp)

def create_ocr_ditectory():
    directory_path = "./converted_pdf"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print("Directory created")
    else:
        print("Directory already exists")

register_blueprints(app)
create_ocr_ditectory()

@app.route("/chat", methods=["POST"])
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
        raw_response = llm.invoke(prompt)
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

# if __name__ == "__main__":
#     ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
#     ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
#     app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
    