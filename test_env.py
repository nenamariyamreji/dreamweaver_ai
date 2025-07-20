import os
from dotenv import load_dotenv

print("WORKING DIR:", os.getcwd())

dotenv_path = os.path.join(os.getcwd(), ".env")
print("Using dotenv at:", dotenv_path)

load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("API_KEY")
print("API_KEY:", api_key)
