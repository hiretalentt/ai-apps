import os

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key is None:
        print("Please set environment variable MISTRAL_API_KEY")
        exit(1)

    model = "mistral-large-latest"

