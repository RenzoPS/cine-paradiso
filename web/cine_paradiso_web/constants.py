import os

from dotenv import load_dotenv

load_dotenv()

WEB_PORT = int(os.getenv('WEB_PORT', '5001'))

SECRET_KEY = os.getenv('WEB_SECRET_KEY', 'solo-para-desarrollo')

API_URL = os.getenv('API_URL', 'http://localhost:5000/cine_paradiso_api')
