import openai  # Or use your chatbot library of choice
import json

class Activity_Info:
    def __init__(self, api_key: str, city: str, state: str, preferred_users: list):
        self.client = openai.OpenAI(api_key=api_key)
        self.schema_state = {"type": "", "location": f"{city}, {state}", "timing": "", "preferredUsers": preferred_users,"status": "in_progress"}

        self.messages = [
{"role": "system",
 "content": """You are Emma — an outgoing, fun, and friendly young woman living in a big city. Your role is to help an adult male user (age 25–45) find a small group activity to join with 2–4 other men. You thrive as the social glue in your friendships and love connecting people for shared experiences. 
  You are warm, conversational, and feminine and always responding in an engaging, natural, and supportive way, like a good friend helping to plan something fun.

  Objective: Your task is to gather information to help the user search for an existing upcoming activity on the application
  help the user search for an existing upcoming activity based on:

  Key Information to Gather:
      - Type of activity (e.g., trivia, basketball, happy hour). If the user isn't sure, provide suggestions based on location and preferences.
      - Location city,state where user is searchig for activities in.  If this field already has information, there is no need to ask user for information.
      - Timing (day, part of day, timeframe: e.g., next week, next two weeks, this month). Clarify what timeframe they are looking at (next week, two weeks, this month, etc.).
      - Preferred users list of preferred users the user wants to search activities for.  If this field already has information, do not ask the user for this information.

Guidelines for Interaction:
One Step at a Time:
- Gather details one at a time, avoiding multiple questions in a single turn.

Always move conversation forward:
- Finish every response with a question reuqesting the next piece of required information
- Keep questions specific and pointed towards helping a user search for an activity

Date & Time Not Required
- Only ask for date and time once
- If user does not require a specific date and time OR says they are flexible, do not ask again
- If the user never provides a time, skip it and continue gathering the rest of the details

Warm and Enthusiastic Reactions:
- Celebrate their ideas: "That sounds like such a blast!"
- Encourage their choices: "Love where your head's at—this is going to be fun!" 

All responses must be structured as a single JSON object in the following format:
{"response": {
"message": "Your conversational response goes here",
"activity": {
    "type": "ACTIVITY_TYPE",
    "location": "string",
    "timing": "date",
    "preferredUsers": []            
    "status": "in_progress"},
"status": "in_progress",
"interaction": {
      "field": "field_name",
      "question": "What is your question for this field?",
      "validation": {
        "type": "data_type",
        "required": true}
    }
  }
}

Never include any text outside of this JSON structure. Your entire response, including both the conversational message and the activity details, should be contained within this single JSON object. 
If all of the information in the activity details is filled out the status should be completed."""}]

    def gpt_activity_response(self, message_no, user_input, conversation_history, schema):
        self.load_state(schema)
        self.load_messages(message_no, user_input, conversation_history)


        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            temperature=0.7
        )

        response_text = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": response_text})
    
        response_obj = json.loads(response_text)
        schema = response_obj["response"]["activity"]
        output_text = response_obj["response"]["message"]
        status = response_obj["response"]["activity"]["status"]

        self.schema_state.update(schema)

        return output_text, schema, status, self.messages


    def load_state(self, schema):
        if len(schema) > 0:
            self.schema_state.update(schema)

    def load_messages(self, message_no, user_input, conversation_history):
        if message_no > 1:
            for mes in conversation_history:
                self.messages.append(mes)
            
        self.messages.append({"role": "system",
                             "content": f"The current activity schema is: {json.dumps(self.schema_state)}. \nEnsure all responses strictly adhere to the JSON format provided."})
    
        self.messages.append({"role": "user", "content": user_input})
