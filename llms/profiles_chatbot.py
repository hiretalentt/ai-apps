import os
from mistralai import Mistral
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class ChatBot:

    def __init__(self, _api_key, model):
        self.api_key = _api_key
        self.model = model
        self.conversation_history = []
        self.mistral_client = Mistral(api_key=api_key)
        self.initialize_context()

    def initialize_context(self):
        try:

            # MongoDB Connection
            mongo_client = MongoClient(os.getenv("MONGODB_URI"))
            db = mongo_client["app-dev"]
            profiles_collection = db["profiles"]
            profiles = profiles_collection.find()
            profiles_in_string_format = []
            for profile in profiles:
                # print("Raw profile from DB:", profile)
                firstname = profile.get("firstName", "Unknown")
                lastname = profile.get("lastName", "N/A")
                position = profile.get("areaOfExpertise", "N/A")
                summary = f"Profile: Name - {firstname + " " + lastname}, Position - {position}"
                profiles_in_string_format.append(summary)

            profiles_in_system_context = "\n".join(profiles_in_string_format)
            profile_message = {
                "role": "system",
                "content": profiles_in_system_context
            }
            self.conversation_history.append(profile_message)

        except Exception as e:
            print(f"Error fetching profiles: {e}")
            return []

    def get_user_input(self):
        user_input = input("\nYou: ")
        user_message = {
            "role": "user",
            "content": user_input
        }
        self.conversation_history.append(user_message)
        return user_message

    def send_request(self):
        stream_response = self.mistral_client.chat.stream(
            model=self.model,
            messages=self.conversation_history
        )
        buffer = ""
        for chunk in stream_response:
            # print(..., end="", flush=True)
            content = chunk.data.choices[0].delta.content
            print(content, end="")
            buffer += content

        if buffer.strip():  # Only add if there's actual content
            assistant_message = {
                "role": "assistant",
                "content": buffer
            }
            self.conversation_history.append(assistant_message)

    def run(self):
        while True:
            self.get_user_input()
            self.send_request()


if __name__ == "__main__":
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key is None:
        print("Please set environment variable MISTRAL_API_KEY")
        exit(1)

    chat_bot = ChatBot(api_key, "mistral-large-latest")
    chat_bot.run()
