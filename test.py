from flask import Flask, request, redirect
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

    return redirect('http://dwidrihfe.csc.fi/success.html')

@app.errorhandler(Exception)
def exception_handler(error):
    with open("/data/www/testserver/error", "a+") as f:
        f.write(repr(error))
    return 'Error logged'