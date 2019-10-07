from flask import Flask, request
import datetime
app = Flask(__name__)

@app.route("/")
def hello():
    return "hello"

@app.route("/", methods=['POST'])
def post_received():
    date = datetime.datetime.now()
    with open("/data/www/testserver/formdata/form_" + str(date), "w+") as f:
        f.write(str(request.form.to_dict()))

    return 'thanks'

@app.errorhandler(Exception)
def exception_handler(error):
    with open("/data/www/testserver/error", "a+") as f:
        f.write(repr(error))
    return 'Error logged'