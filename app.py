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

def generate_activity_info(message_no, message, conversation_history, schema, city, state, api_key, preferred_users):
    activity_info = Activity_Info(api_key, city, state, preferred_users)
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
    preferred_users = ["Alex Vans", "Thaddeus"]
    ##planner = EventPlanner(api_key, city, state)
    completed_flag = False
    activity_recommendation = False

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
            output_text, return_schema, status = generate_activity_info(message_no, message, conversation_history, schema, city, state, api_key, preferred_users)
            
            ## If activity status is done, then resets the activity and sets completed_flag == True
            bot_reply = output_text.strip()
            if status == "finished" or status == "completed" or status == "complete":
                print("activity completed")
                completed_flag = True
                session_reset()
                activity_recommendation = generate_activity_search(message, city, state, api_key, return_schema)
                ##bot_reply = bot_reply + "\n" 
                ##bot_reply = bot_reply + activity_recommendation
                print(activity_recommendation)
                print(type(activity_recommendation))
                print("reloading page with recommendation")


            return jsonify({"reply": bot_reply, "schema": return_schema, "completed": completed_flag, "activity_recommendations": activity_recommendation})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/activities')
def activities():
    # Example list of activity dicts
    activity_list = [
{"activity_id": "1",
"description":"A fun and competitive game of tennis",
"level_of_flexibility":"Specific date",
"location":"Quincy Park, Arlington, Virginia",
"maxParticipants":5,
"minParticipants":3,
"name":"Tennis Titans at Quincy",
"scheduledAt":"This Wednesday",
"status":"completed",
"type":"Outdoor Sports",
"preferredUsers": ["Rafael", "Novak"]},

{"activity_id": "2",
"description": "A fun and adventurous hiking activity",
"level_of_flexibility":"Flexible",
"location": "W&OD Trail in Shirlington, VA",
"maxParticipants": 5,
"minParticipants": 3,
"name": "Arlington Adventure Hike",
"scheduledAt": "N/A",
"status": "completed",
"type": "Outdoor Activity",
"preferredUsers": ["Thaddeus", "Sohom"]},

{"activity_id": "3",
"description":"Watching a basketball game",
"level_of_flexibility":"specific date and time",
"location":"Dudleys in Shirlington, Virginia",
"maxParticipants":5,
"minParticipants":3,
"name":"Saturday Hoops at Dudley's",
"scheduledAt":"this Saturday at 7 pm",
"status":"completed",
"type":"Watching sports",
"preferredUsers": []},

{"activity_id": "4",
"description":"Bowling activity",
"level_of_flexibility":"Low",
"location":"Lucky Strike Tysons Corner",
"maxParticipants":5,
"minParticipants":4,
"name":"Friday Night Strikes",
"scheduledAt":"This Friday at 7:30 pm",
"status":"completed",
"type":"Bowling",
"preferredUsers": ["Alex Vans", "Derek"]},

{"activity_id": "5",
 "description":"A fun-filled trivia night with friends.",
 "level_of_flexibility":"Low",
 "location":"Arlington, Virginia",
 "maxParticipants":4,
 "minParticipants":3,
 "name":"Friday Night Trivia Challenge",
 "scheduledAt":"Friday night",
 "status":"completed",
 "type":"Bar Game",
 "preferredUsers": ["Ken","James"]},

{"activity_id": "6",
 "description":"A fun day of hiking at Rock Creek Park",
 "level_of_flexibility":"Low",
 "location":"Rock Creek Park, Washington D.C.",
 "maxParticipants":6,
 "minParticipants":3,
 "name":"D.C. Hiking Adventure",
 "scheduledAt":"This Sunday at 12 pm",
 "status":"completed",
 "type":"Outdoor Fitness & Adventures",
 "preferredUsers":["William Sherman","Ulysses Grant"]},

 {"activity_id": "7",
  "description":"A fun pop up comedy show in the DC area.",
  "level_of_flexibility":"Low",
  "location":"Fitness studio, Washington D.C.",
  "maxParticipants":6,
  "minParticipants":3,
  "name":"Don’t tell comedy",
  "scheduledAt":"May 24, 2025",
  "status":"completed",
  "type":"Arts, Entertainment & Culture", 
  "preferredUsers":["Derek Bratcher"]},

 {"activity_id": "8",
  "description":"Fun time playing Billiards in D.C.",
  "level_of_flexibility":"Flexible",
  "location":"Bedrock Billiards Washington D.C.",
  "maxParticipants":6,
  "minParticipants":3,
  "name":"Billiards night",
  "scheduledAt":"N/A",
  "status":"completed",
  "type":"Indoor/Bar Games",
  "preferredUsers":["Derek Bratcher", "Ryan Oberleitner"]},

 {"activity_id": "9",
 "description":"A target shooting event at Peacemaker National Training Center",
 "level_of_flexibility":"Flexible",
 "location":"Peacemaker National Training Center, Washington D.C.",
 "maxParticipants":5,
 "minParticipants":3,
 "name":"Bullseye at Peacemaker",
 "scheduledAt":"N/A",
 "status":"completed",
 "type":"Outdoor activities", 
 "preferredUsers":["Alex Vans"]}, 

 {"activity_id": "10",
 "description":"A fun and playful board game night with friends",
 "level_of_flexibility":"low",
 "location":"The Board Room, Dupont",
 "maxParticipants":6,
 "minParticipants":3,
 "name":"Board Games Bonanza",
 "scheduledAt":"May 27, 2025",
 "status":"completed",
 "type":"Playing Sports", 
 "preferredUsers":["Ryan Oberleitner", "Jack Rockaway"]}
]
    return render_template("activity.html", activity_list=activity_list)

if __name__ == '__main__':
    app.run(debug=True)
