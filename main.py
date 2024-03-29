from flask import Flask, request, redirect
import datetime
import logging
import json
import os
from format_json import hierarchize
app = Flask(__name__)

if __name__ != '__main__':
    logHandler = logging.FileHandler('/data/www/infraserver/gunicorn.error')
    logHandler.setLevel(logging.WARN)
    app.logger.addHandler(logHandler)
    app.logger.setLevel(logging.WARN)

@app.route('/sent', methods=['POST'])
def post_received():

    def copy_values(data, firstFields=True, index=""):
        # 3b fields from source (2a)
        
        source_prefix = "infraCon"
        target_prefix = "SerPoint"
        fields = ["Tel", "Email", "Post","Municipality", "Country"]
        langs_field = ["Name","Descr","Info","Terms"]
        

        # 3c fields from source (2b)
        if not firstFields:
            source_prefix = "CoOrg"
            target_prefix = "CoOrgOther"
            fields = ["ID", "Isni"]
            langs_field = ["Name"]
        
        langs = ["Fi","En","Sv"]
        fields = fields + [field + lang for field in langs_field for lang in langs]


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
	
@app.route('/hook', methods=['POST'])
def webhook():
    BRANCH = os.getenv('BRANCH')
    if 'ref' in request.json and request.json['ref'].split('/')[-1] == BRANCH:
        if request.json['repository']['name'].split('-')[-1] == 'backend':
            os.chdir('/data/www/infraserver')
            # Make sure to clean git status and switch to correct branch
            os.system('git stash')
            os.system(f'git checkout {BRANCH}')
            os.system('git pull')
            os.system('systemctl restart infraform.service')
            app.logger.log(logging.WARN, f'INFO: Backend service restarted after push to {BRANCH}')
        elif request.json['repository']['name'].split('-')[-1] == 'frontend':
            os.chdir('/data/www/infraform')
            os.system('git stash')
            os.system(f'git checkout {BRANCH}')
            os.system('git pull')
            app.logger.log(logging.WARN, f'INFO: New frontend version pulled after push to {BRANCH}')
    return ''


@app.errorhandler(Exception)
def exception_handler(error):
    app.logger.exception("----------" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "----------")
    return 'There was an error while submitting the request.\nThe error has been logged'