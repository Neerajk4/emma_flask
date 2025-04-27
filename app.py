from flask import Flask, render_template, request, jsonify, session
import openai
import os
from chat_info2 import EventPlanner
from dotenv import load_dotenv

app = Flask(__name__)
## Flask app to test out chatbot functionality to set up activities for Emma

# Set your OpenAI API key
load_dotenv() 
api_key = os.environ.get("API_KEY1")
app.secret_key = os.environ.get('SECRET_KEY')

def session_reset():
    session.clear()  # Clear session on a new visit
    session["conversation_history"] = []  # Initialize history
    session["message_number"] = 0  # Track number of messages
    session["schema"] = {} 

## Index template page.  Uses a global dictionary using session to store key variables. 
@app.route('/')
def index():
    session.clear()  # Clear session on a new visit
    session["conversation_history"] = []  # Initialize history
    session["message_number"] = 0  # Track number of messages
    session["schema"] = {}  # Track activity schema
    return render_template('index.html')


## post request to ping gpt and get information back
@app.route('/chat', methods=['POST'])
def chat():
    city = "Arlington"
    state = "Virginia"
    planner = EventPlanner(api_key, city, state)
    completed_flag = False

    # Retrieve history from session
    conversation_history = session.get("conversation_history", [])
    message_no = session.get("message_number", 1)
    schema = session.get("schema", {})

    # gets message from request from index.html
    message = request.json.get("message")
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        # gets info from planner.chat which sends pings OpenAI api to get gpt response
        response_text, message, schema, status, prompt_token_count, token_count, conversation_history = planner.chat(message_no, message, conversation_history, schema)
        # Increment message count
        message_no = message_no + 3  

        # Stores information into session dictionary
        session["conversation_history"] = conversation_history
        session["message_number"] = message_no
        session["schema"] = schema

        ## If activity status is done, then resets the activity and sets completed_flag == True
        bot_reply = message.strip()
        if status == "finished" or status == "completed" or status == "complete":
            completed_flag = True
            session_reset()
        
        return jsonify({"reply": bot_reply, "schema": schema, "completed": completed_flag})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
