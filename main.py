from flask import Flask, request, redirect
import datetime
import logging
import json
from format_json import hierarchize
app = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('/data/www/infraserver/gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

@app.route("/sent", methods=['POST'])
def post_received():

    def copy_values(data, firstFields=True, index=""):
        # 3b fields from source (2a)
        source_prefix = "infraCon"
        target_prefix = "SerPoint"
        fields = ["Name", "Descr", "Tel", "Email", "Post", "Info", "Terms", "Municipality", "Country"]

        # 3c fields from source (2b)
        if not firstFields:
            source_prefix = "CoOrg"
            target_prefix = "CoOrgOther"
            fields = ["Name", "ID", "Isni"]

        for field in fields:
            data[target_prefix + field + index] = data[source_prefix + field]

        return data

    date = datetime.datetime.now()
    date_str = f"{date.year}-{date.month}-{date.day}_{date.hour}-{date.minute}-{date.second}"
    filename = "form_" + date_str + ".json"
    data = request.form.to_dict()
    extras = int(data["extra-services"])
    del data["extra-services"]

    # For each extra service
    for postfix in ([""] + [idx for idx in range(extras)]):
    # Check if the box for different info is checked. Copy values if not
        if not int(data["SerPointSame" + str(postfix)]):
            data = copy_values(data, index=str(postfix))

        if not int(data["SerCoOrg" + str(postfix)]):
            data = copy_values(data, firstFields=False, index=str(postfix))

    with open("/data/www/infraserver/formdata/" + filename, "w+") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8').decode())

    hierarchize("/data/www/infraserver/formdata", filename, "/data/www/infraserver/formdata")

    return redirect('http://dwidrihfe.csc.fi/success.html')

@app.errorhandler(Exception)
def exception_handler(error):
    with open("/data/www/infraserver/error.serverlog", "a+") as f:
        f.write(repr(error) + "\n")
    return 'Error logged'