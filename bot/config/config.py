import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

CHILL_STATION_GUILD_ID = 1356994231918530690

AUTO_MUTE_WARNING_THRESHOLD = 3
AUTO_MUTE_DURATION_MINUTES = 60

BANNED_WORDS = [
    "lồn",
    "buồi",
    "cặc",
    "địt",
    "đjt",
    "dit",
    "l*n",
    "l`n",
    'đụ',
]

NUMBER_OF_MEMBER_REQUIRED_FOR_PN = 300

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}