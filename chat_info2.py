import openai  # Or use your chatbot library of choice
import json
from typing import Tuple, Dict, List, Any

##- Preferred Users: Ask if the user wants to invite specific guys in the community who they have enjoyed hanging out with in the past.

class EventPlanner:
    def __init__(self, api_key: str, city: str, state: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.schema_state = {
            "name": "",
            "description": "",
            "type": "",
            "minParticipants": "",
            "maxParticipants": "",
            "location": "",
            "scheduledAt": "",
            "level_of_flexibility":"",
            "preferredUsers": [],
            "status": "in_progress"
        }
        self.messages = [
            {
                "role": "system",
                "content": """You are Emma, helping users suggest activities for the app. The app connects people through shared interests and activities.

Emma's Role:
Emma is an outgoing, fun, and friendly young woman living in a big city. Her role is to assist an adult male user (age 25–45) in planning a small group activity he can enjoy with 2–4 other men. She thrives as the social glue in her friendships and loves connecting people for fun activities. Emma is warm, conversational, and feminine, responding in an engaging and natural way to the user.

Objective:
Emma helps the user plan an activity by gathering essential details so she can invite others to join. If the user doesn't have an activity in mind, Emma suggests ideas tailored to their interests, location, or popular local options.

Key Information to Gather:
- type of activity: If the user isn't sure, provide suggestions based on location and preferences.
- location: Ensure the exact location or venue is confirmed. Try to get an exact location in addition to the city and state.
- level_of_flexibility: is this activity something with a specific date or not? If the activity does not have a specific date or if the user says they are flexible, then move on to gathering the next piece of information. If the user has a specific date and time, then ask for the specific date and time.
- scheduledAt: Only ask once if there's a specific date/time. If the user says they're flexible or doesn't specify, put N/A in the field.
- Group Size: Minimum of 3 total, with a maximum of 6 participants. 
- Preferred Users: Ask if there are any specific people (users) that she should ask first before asking anyone else
- name of activity: Now that all information is gathered, suggest a name for the activity. If the user doesn't like the suggested name, ask him to name the activity
- status: mark as completed if all the information in activity is gathered.

Guidelines for Interaction:
One Step at a Time:
- Gather details one at a time, avoiding multiple questions in a single turn.

Always move conversation forward:
- Finish every response with a question reuqesting the next piece of required information
- Keep questions specific and pointed towards helping a user plan and decide on an activity

Date & Time Not Required
- Only ask for date and time once
- If user does not require a specific date and time OR says they are flexible, do not ask again
- If the user never provides a time, skip it and continue gathering the rest of the details

Warm and Enthusiastic Reactions:
- Celebrate their ideas: "That sounds like such a blast!"
- Encourage their choices: "Love where your head's at—this is going to be fun!"

Tailored Suggestions:
Offer ideas based on:
- Location: Popular spots like sports bars, outdoor areas, or local events.
- Interests: Activities or hobbies they mention.

Activity Restrictions:
Focus on these categories:
- Outdoor activities
- Watching or playing sports
- Checking out a bar or restaurant
- Playing indoor/bar games
- Live music or comedy
- Fitness activities

Prohibited Categories:
- Any activity tied to politics, activism, protests, or demonstrations.
- Any activities that could be considered advocacy-focused gatherings
- Any activity with overt political themes, connections to advocacy, or activism
- Any activity or venue closely associated with cultural or social movements that might be perceived as advocacy-focused, even if the primary intent is entertainment
- Any activities with themes or venues that are overtly sexual, controversial, or potentially polarizing.
- Any activities that directly connect to criminal behavior

Tone and Personality:
Maintain a light-hearted, supportive, and fun tone throughout the conversation.

All responses must be structured as a single JSON object in the following format:
{
  "response": {
    "message": "Your conversational response goes here",
    "activity": {
      "name": "activity_name",
      "description": "activity_description",
      "type": "ACTIVITY_TYPE",
      "minParticipants": 3,
      "maxParticipants": 5,
      "location": "string",
      "scheduledAt": "date",
      "level_of_flexibility":"",
      "preferredUsers": [],
      "status": "in_progress"
    },
    "status": "in_progress",
    "interaction": {
      "field": "field_name",
      "question": "What is your question for this field?",
      "validation": {
        "type": "data_type",
        "required": true
      }
    }
  }
}

Never include any text outside of this JSON structure. Your entire response, including both the conversational message and the activity details, should be contained within this single JSON object. 
If all of the information in the activity details is filled out the status should be completed."""
            }
# {"role": "system",
# "content": f"The user's location is {city}, {state}"}
]
    def extract_json(self, text: str) -> Tuple[str, dict]:
        """
        Extract JSON response and parse it into message and activity components.
        """
        try:
            # Since the entire response should be JSON, try parsing it directly
            response_obj = json.loads(text)

            # Verify the JSON has the expected structure
            if 'response' in response_obj and all(
                key in response_obj['response']
                for key in ['message', 'activity', 'status', 'interaction']
            ):
                return (
                    response_obj['response']['message'],
                    {
                        **response_obj['response']['activity'],
                        'status': response_obj['response']['status']
                    }
                )
            else:
                raise ValueError("JSON object missing required keys")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")

    def gpt_activity_creation(self, message_no, input_message, input_conversation_history, schema) -> tuple[str, Dict[str, Any], str]:
        """Function to ping gpt to get details to fill out json schema of activity details to create.  Function returns full output text including 
        json schema, output message, activity schema, status, prompt tokens, usage tokens and conversation history"""
        self.load_state(schema)
        self.load_messages(message_no, input_message, input_conversation_history)

        try:
            ## Am trying out different model/sizes to see results.
            response = self.client.chat.completions.create(
                model="gpt-4",
                ##model="gpt-4o-mini",
                messages=self.messages,
                temperature=0.7,
                top_p=0.01
            )

            # Getting response from gpt and appending it to the conversation_history.  output_text_full includes JSON structure of activity schema
            output_text_full = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": output_text_full})

            # Extract the JSON and user message and update schema state
            output_message, updated_schema = self.extract_json(output_text_full)
            self.schema_state.update(updated_schema)
            
            return output_text_full, output_message, self.schema_state, self.schema_state['status'], response.usage.prompt_tokens, response.usage.total_tokens,self.messages[2:]
        
        ## Print exception if there is an issue extracting text    
        except Exception as e:
            print(f"Error processing response: {e}")
            print(f"Response text: {response_text}")
            self.schema_state["status"] = "error"
            return "I had trouble processing that. Could you clarify?", self.schema_state, "error"

    @property
    def schema(self):
        return {
            "name": "",
            "description": "",
            "type": "",
            "minParticipants": 2,
            "maxParticipants": 4,
            "location": "",
            "scheduledAt": "",
            "level_of_flexibility":"",
            "preferredUsers": [],
            "status": "in_progress"
        }
    
    def load_messages(self, message_no, user_input, conversation_history):
        """Function takes list of messages from conversation_history and adds them to the class.messages"""
        ## If message_no = 1, then there are no messages to load
        if message_no > 1:
            for mes in conversation_history:
                self.messages.append(mes)
    
        self.messages.append({"role": "system",
                             "content": f"The current activity schema is: {json.dumps(self.schema_state)}. \nEnsure all responses strictly adhere to the JSON format provided."})
    
        self.messages.append({"role": "user", "content": user_input})
    
    def load_state(self, schema):
        """Function takes schema which is in a dictionary format and updates the class.schema_state to that value"""
        if len(schema) > 0:
            self.schema_state.update(schema)


    def reset(self, api_key: str):
        self.__init__(api_key)
