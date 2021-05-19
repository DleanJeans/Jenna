from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
TESTING = os.getenv('TESTING')
LOCAL = os.getenv('LOCAL')
HOME_GUILD = int(os.getenv('HOME_GUILD'))
EMOTES_BUFFER_GUILD = int(os.getenv('EMOTES_BUFFER_GUILD'))