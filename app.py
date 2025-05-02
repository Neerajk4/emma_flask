from flask import Flask, render_template, request, jsonify, session
import openai
import os
from chat_info2 import EventPlanner
from activity_info_class import Activity_Info
from activity_search_class import Activity_Search
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

def generate_response(message_no, message, conversation_history, schema, city, state, api_key):
    planner = EventPlanner(api_key, city, state)
    # gets info from planner.chat which sends pings OpenAI api to get gpt response
    response_text, return_message, return_schema, status, prompt_token_count, token_count, conversation_history = planner.chat(message_no, message, conversation_history, schema)
    # Increment message count
    message_no = message_no + 3  
    # Stores information into session dictionary
    session["conversation_history"] = conversation_history
    session["message_number"] = message_no
    session["schema"] = return_schema
    return return_message, return_schema, status

def generate_activity_info(message_no, message, conversation_history, schema, city, state, api_key):
    activity_info = Activity_Info(api_key, city, state)
    output_text, return_schema, status, conversation_history = activity_info.gpt_activity_response(message_no, message, conversation_history, schema)

    # Increment message count
    message_no = message_no + 3  
    # Stores information into session dictionary
    session["conversation_history"] = conversation_history
    session["message_number"] = message_no
    session["schema"] = return_schema
    return output_text, return_schema, status

def generate_activity_search(message, city, state, api_key, schema):
    print("load activity_class")
    activity_search = Activity_Search(api_key, city, state, schema)
    print("activity class loaded")
    activity_recommendation = activity_search.gpt_activity_search()
    print("gpt pinged")
    return activity_recommendation

## Index template page.  Uses a global dictionary using session to store key variables. 
@app.route('/')
def index():
    session.clear()  # Clear session on a new visit
    session["conversation_history"] = []  # Initialize history
    session["message_number"] = 1  # Track number of messages
    session["schema"] = {}  # Track activity schema
    return render_template('index.html')


## post request to ping gpt and get information back
@app.route('/chat', methods=['POST'])
def chat():
    city = "Arlington"
    state = "Virginia"
    ##planner = EventPlanner(api_key, city, state)
    completed_flag = False

    # Retrieve history from session
    conversation_history = session.get("conversation_history", [])
    message_no = session.get("message_number", 1)
    schema = session.get("schema", {})

    # gets message from request from index.html
    data = request.get_json()
    mode = data.get('mode', 'activity_search')  # Default to activity_search if not provided
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        if mode == 'activity_creation':
            return_message, return_schema, status = generate_response(message_no, message, conversation_history, schema, city, state, api_key)

            ## If activity status is done, then resets the activity and sets completed_flag == True
            bot_reply = return_message.strip()
            if status == "finished" or status == "completed" or status == "complete":
                completed_flag = True
                session_reset()
        
            return jsonify({"reply": bot_reply, "schema": return_schema, "completed": completed_flag})
        
        else:
            output_text, return_schema, status = generate_activity_info(message_no, message, conversation_history, schema, city, state, api_key)
            
            ## If activity status is done, then resets the activity and sets completed_flag == True
            bot_reply = output_text.strip()
            if status == "finished" or status == "completed" or status == "complete":
                print("activity completed")
                completed_flag = True
                session_reset()
                activity_recommendation = generate_activity_search(message, city, state, api_key, return_schema)
                bot_reply = bot_reply + "\n" 
                bot_reply = bot_reply + activity_recommendation
                print("reloading page with reommendation")


            return jsonify({"reply": bot_reply, "schema": return_schema, "completed": completed_flag})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
