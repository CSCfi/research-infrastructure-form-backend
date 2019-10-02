from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "hello"

@app.route("/", methods=['POST'])
def post_received():
    return 'thanks'