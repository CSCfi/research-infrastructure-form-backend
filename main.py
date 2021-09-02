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
    print(json.dumps(request.json, sort_keys=False, indent=4))
    print(request.json['repository']['name'].split('-')[-1])
    if request.json['repository']['name'].split('-')[-1] == 'backend' and 'ref' in request.json:
        print(request.json['ref'].split('/')[-1])
        os.system('cd /data/www/infraserver && git pull && sudo systemctl restart infraform.service')
    return ''


@app.errorhandler(Exception)
def exception_handler(error):
    app.logger.exception("----------" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "----------")
    return 'There was an error while submitting the request.\nThe error has been logged'