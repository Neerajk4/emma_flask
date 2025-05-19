# Import Statements
from flask import Flask, render_template, request, jsonify, session
import openai
import os
from chat_info2 import EventPlanner
from activity_info_class import Activity_Info
from activity_search_class import Activity_Search
from dotenv import load_dotenv

from activity_list import activities2

## Flask app to test out chatbot functionality to set up activities for Emma
app = Flask(__name__)

# Set your OpenAI API key
# app.secret key is only for flask purposes.
load_dotenv() 
api_key = os.environ.get("API_KEY1")
app.secret_key = os.environ.get('SECRET_KEY')

# Function to reset session parameters
def session_reset():
    """Function clears session on a new visit.  This includes clearing the conversation_history, message_number and 
    activity schema which is in a json format."""
    session.clear()  
    session["conversation_history"] = [] 
    session["message_number"] = 1 
    session["schema"] = {} 

# Function to send gpt response for activity creation
def generate_activity_creation(message_no, input_message, input_conversation_history, input_schema, city, state, api_key):
    """Function creates EventPlanner class which helps user create an activity.  Using input information, planner.chat
    will ping GPT to get appropriate response to users question in order to fill out activity_schema"""
    planner = EventPlanner(api_key, city, state)
    # gets info from planner.chat which sends pings OpenAI api to get gpt response
    response_text, return_message, return_schema, status, prompt_token_count, token_count, conversation_history = planner.gpt_activity_creation(message_no, input_message, input_conversation_history, input_schema)
    # Increment message count
    message_no = message_no + 3  
    # Stores information into session dictionary
    session["conversation_history"] = conversation_history
    session["message_number"] = message_no
    session["schema"] = return_schema
    return return_message, return_schema, status

# Function to send gpt response for collect activity info for search
def generate_activity_search_info(message_no, input_message, input_conversation_history, input_schema, city, state, api_key, preferred_users):
    """Function creates Activity_Info class which helps user collect information to search for an activity. Using input information, 
    gpt_activity_response will ping GPT to get appropriate response to users question in order to fill out activity_schema"""

    activity_info = Activity_Info(api_key, city, state, preferred_users)
    return_message, return_schema, return_status, conversation_history = activity_info.gpt_activity_response(message_no, input_message, input_conversation_history, input_schema)

    # Increment message count
    message_no = message_no + 3  
    # Stores information into session dictionary
    session["conversation_history"] = conversation_history
    session["message_number"] = message_no
    session["schema"] = return_schema

    return return_message, return_schema, return_status

# Function to send gpt response for activity recommendations for users
def generate_activity_search(message, city, state, api_key, schema, activities2):
    """Function creates Activity_Search class which helps search for an activity based on their activity preferences. Function uses 
    gpt_activity_search will ping GPT to get recommended activities for users"""
    activity_search = Activity_Search(api_key, city, state, schema, activities2)
    activity_recommendation = activity_search.gpt_activity_search()
    return activity_recommendation

## Index template page.  Uses a global dictionary using session to store key variables. 
@app.route('/')
def index():
    """Clears session on a new visit, initializes conversation history, sets number of messages and clears activity schema"""
    session.clear()  
    session["conversation_history"] = []  
    session["message_number"] = 1  
    session["schema"] = {}  
    return render_template('index.html')


## post request to ping gpt and get information back
@app.route('/chat', methods=['POST'])
def chat():
    city = "Arlington"
    state = "Virginia"
    preferred_users = ["Alex Vans", "Thaddeus"]
    
    # Sets flags for determining if all information is collected and if activity recommendations are needed.
    completed_flag = False
    activity_recommendation = False

    # Retrieve history from session
    conversation_history = session.get("conversation_history", [])
    message_no = session.get("message_number", 1)
    schema = session.get("schema", {})

    # gets message from request from index.html
    data = request.get_json()
    mode = data.get('mode', 'activity_search')  
    message = data.get('message', '')

    # Returns 400 error if no payload for message
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        # There are two modes activity_creation and activity_search.  
        if mode == 'activity_creation':
            return_message, return_schema, status = generate_activity_creation(message_no, message, conversation_history, schema, city, state, api_key)

            ## If activity status is done, then resets the activity and sets completed_flag == True
            bot_reply = return_message.strip()
            if status == "finished" or status == "completed" or status == "complete":
                completed_flag = True
                session_reset()
        
            return jsonify({"reply": bot_reply, "schema": return_schema, "completed": completed_flag})
        
        # logic for activity_search mode
        else:
            return_message, return_schema, status = generate_activity_search_info(message_no, message, conversation_history, schema, city, state, api_key, preferred_users)
            
            ## If activity status is done, then resets the activity and sets completed_flag == True
            bot_reply = return_message.strip()
            if status == "finished" or status == "completed" or status == "complete":
                completed_flag = True
                session_reset()
                activity_recommendation = generate_activity_search(message, city, state, api_key, return_schema, activities2)

            return jsonify({"reply": bot_reply, "schema": return_schema, "completed": completed_flag, "activity_recommendations": activity_recommendation})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/activities')
def activities():
    # Example list of activity dicts
    return render_template("activity.html", activity_list=activities2)

if __name__ == '__main__':
    app.run(debug=True)
