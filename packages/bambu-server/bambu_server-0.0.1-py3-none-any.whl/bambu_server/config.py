from flask import Flask
from celery import Celery
from dotenv import load_dotenv
import os

try:
    load_dotenv()
except:
    pass

app = Flask(__name__)
redis_uri = os.environ['BAMBU_REDIS_URI']
celery = Celery(__name__, broker=redis_uri, backend=redis_uri)
