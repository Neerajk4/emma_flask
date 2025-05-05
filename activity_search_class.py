import openai  # Or use your chatbot library of choice
import json

class Activity_Search:
    def __init__(self, api_key: str, city: str, state: str, activity_preferences: dict):

        self.client = openai.OpenAI(api_key=api_key)

        self.messages = []
        self.activities = [
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
"preferredUsers": ["Alex", "Derek"]},

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
 "description":"A fun happy hour with friends on a Sunday.",
 "level_of_flexibility":"Low",
 "location":"Astro's Beer Hall Arlington, Virginia",
 "maxParticipants":5,
 "minParticipants":3,
 "name":"Sunday Funday Happy Hour",
 "scheduledAt":"This Sunday",
 "status":"completed",
 "type":"Bar or Restaurant",
 "preferredUsers":["Robert","Ulysses"]},

 {"activity_id": "7",
  "description":"A fun day of tennis at Hooes Road Park. All skill levels welcome!",
  "level_of_flexibility":"Specific date",
  "location":"Hooes Road Park, Springfield, Virginia",
  "maxParticipants":5,
  "minParticipants":3,
  "name":"Sunday Tennis Showdown at Hooes Park",
  "scheduledAt":"This Sunday",
  "status":"completed",
  "type":"Tennis", 
  "preferredUsers":[]},

 {"activity_id": "8",
  "description":"Trail running in Shenandoah National Park",
  "level_of_flexibility":"specific date",
  "location":"Shenandoah National Park, Virginia",
  "maxParticipants":5,
  "minParticipants":3,
  "name":"Shenandoah Sprint",
  "scheduledAt":"this Friday",
  "status":"completed",
  "type":"Outdoor activities",
  "preferredUsers":[]},

{"activity_id": "9",
 "description":"A fun and relaxing wine tasting event",
 "level_of_flexibility":"Flexible",
 "location":"Stone Tower Winery Leesburg, Virginia",
 "maxParticipants":5,
 "minParticipants":3,
 "name":"Leesburg Vine Vibes",
 "scheduledAt":"N/A",
 "status":"completed",
 "type":"Wine Tasting", 
 "preferredUsers":["Jason","Derek"]},

 {"activity_id": "10",
 "description":"A fun and energetic soccer game.",
 "level_of_flexibility":"low",
 "location":"Bluemont Park, Arlington, Virginia",
 "maxParticipants":5,
 "minParticipants":3,
 "name":"Sunday Soccer at Bluemont",
 "scheduledAt":"Sunday afternoon at 1 pm",
 "status":"completed",
 "type":"Playing Sports", 
 "preferredUsers":[]}
]

        self.activity_string = f"""You are Emma — an outgoing, fun, and friendly young woman living in a big city. Your role is to help an adult male user (age 25–45) find a small group activity to join with 2–4 other men. You thrive as the social glue in your friendships and love connecting people for shared experiences.
  You are warm, conversational, and feminine and always responding in an engaging, natural, and supportive way, like a good friend helping to plan something fun.

  Objective: Your task is to help the user search for an existing upcoming activity based on their preferences.  Their preferences will include the 
  following information:

  User Preferences:
      - type of activity (e.g., trivia, basketball, happy hour). This is the main criteria to match an activity.
      - location (city, neighborhood, and willingness to travel). 
      - timing (day, part of day, timeframe: e.g., next week, next two weeks, this month). 
      - preferredUsers (if they want to join activities where specific people are participating). 

The user is looking for an activity that best suits their preferences: {activity_preferences}. Here is a list of activities in JSON format:

{self.activities}"""
        
        self.activity_string2 = """Which activity is the best match for this user and why? Return your response in JSON with the fields: activity_id, name, reason.

If a match exists, present 1 upcoming activity that best fit their request.

If no perfect match exists, suggest related or similar activities they might enjoy.

If no relevant activities are available, suggest to the user to switch to the activity search state.

Always stay casual, kind, warm, and focused on helping the user find a fun group to join.

All responses must be structured as a single JSON object in the following format:

{"name": "name of activity", 
 "activity_id": 3,
 "reason": "reason why activity is a good match for user"
}

Never include any text outside of this JSON structure. Your entire response, including both the conversational message and the activity details, should be contained within this single JSON object.
If all of the information in the activity details is filled out the status should be completed."""

    def gpt_activity_search(self):
        self.load_messages()

        response = self.client.chat.completions.create(model="gpt-4o-mini",messages=self.messages,temperature=0.7)
        response_text = response.choices[0].message.content
        return response_text


    def load_messages(self):
        full_string = self.activity_string + self.activity_string2
        self.messages.append({"role": "system","content": full_string})