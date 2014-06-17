from flask import Flask

app = Flask(__name__)
app.config.from_object('settings')
app.config.from_pyfile('settings.py')

@app.route('/')
def hello_world():
    return 'Hello World!'