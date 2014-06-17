from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('settings')
app.config.from_pyfile('settings.py')

@app.route('/')
def hello_world():
    return 'Hello World!'