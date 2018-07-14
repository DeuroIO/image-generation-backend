#!flask/bin/python
from flask import Flask
import os
from apscheduler.schedulers.background import BackgroundScheduler
from aws_operation import check_message

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(check_message, 'interval', seconds=5)
    scheduler.start()

    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
