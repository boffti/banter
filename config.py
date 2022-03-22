from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())


DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_PATH")