import json
from itertools import takewhile

def hierarchize(inputdir, form_file, outputdir):

    # Load the json
    with open(inputdir + "/" + form_file, encoding='utf-8') as f:
        form = json.load(f)

    # Store keys
    keys = form.keys()

    # Assume max 100 services
    extra_services = 0
    for i in range(100):
        # See if the next service exists, increase counter if so
        try:
            form["serNameFi" + str(i)]
            extra_services += 1
        # Break out if last service is reached
        except KeyError as e:
            break

    # Take the fields until the first service field
    common_fields = list(takewhile(lambda x: x != "serNameFi", list(keys)))
    # Take the fields until first service field of second service (or end of file) and remove common fields
    service_fields = list(takewhile(lambda x: x != "serNameFi0" and x != "end_notes", list(keys)))[len(common_fields):]

    # Create the postfixes to loop over
    service_postfixes = [""] + [x for x in range(extra_services)]

    new_dict = {}

    for field in common_fields + ["end_notes"]:
        new_dict[field] = form[field]

    new_dict["services"] = []

    # Keep track of idx with enumerate
    for idx, post in enumerate(service_postfixes):
        new_dict["services"].append({})
        for field in service_fields:
            new_dict["services"][idx][field] = form[field + str(post)]

    # Create output directory if necessary
    import os
    try:
        os.mkdir(outputdir)
    except FileExistsError:
        pass

    with open(outputdir + "/" + form_file, "w+", encoding='utf-8') as f:
        f.write(json.dumps(new_dict, ensure_ascii=False, indent=4).encode("utf-8").decode())


def add_langs(inputdir, form_file, outputdir):
    #Load the json
    with open(inputdir + "/" + form_file, encoding='utf-8') as f:
        form = json.load(f)

    # Store keys
    keys = form.keys()

    new_dict = {}

    # Define fields that need langs
    lang_fields = ['infraDescrSci', 'infraConName', 'infraConDescr', 'infraConInfo', 'infraConTerms', 'CoOrgName']
    service_lang_fields = ['serName', 'serDescr', 'serDescrsci', 'SerPointName', 'SerPointDescr', 'SerPointInfo', 'SerPointTerms',
                           'CoOrgOtherName', 'SerPointName_add', 'SerPointDescr_add', 'SerPointInfo_add', 'SerPointTerms_add']

    
    # Extract common fields
    common_fields = list(takewhile(lambda x: x != "services", list(keys)))
    service_fields = list(form['services'][0].keys())

    # Add langs to fields that need it 
    for field in common_fields:
        # Add keywordSv separately
        if field == 'infraKeywords':
            new_dict[field] = form[field]
            new_dict['infraKeywordsSv'] = ''
        if field not in lang_fields:
            new_dict[field] = form[field]
        else:
            new_dict[field + 'Fi'] = form[field]
            new_dict[field + 'Sv'] = ''
            new_dict[field + 'En'] = ''

    
    # Add langs to service fields that need it
    new_dict['services'] = []
    for idx, service in enumerate(form['services']):
        new_dict['services'].append({})
        for field in service_fields:
            if field not in service_lang_fields:
                new_dict['services'][idx][field] = form['services'][idx][field]
            else:
                new_dict['services'][idx][field + 'Fi'] = form['services'][idx][field]
                new_dict['services'][idx][field + 'Sv'] = ''
                new_dict['services'][idx][field + 'En'] = ''

    # Create output directory if necessary
    import os
    try:
        os.mkdir(outputdir)
    except FileExistsError:
        pass

    with open(outputdir + "/" + form_file, "w+", encoding='utf-8') as f:
        f.write(json.dumps(new_dict, ensure_ascii=False, indent=4).encode("utf-8").decode())

if __name__ == "__main__":
    import sys
    import os

    try:
        cmd = sys.argv[1]
        inputdir = sys.argv[2]
        outputdir = sys.argv[3]
    except IndexError:
        print("usage: format_json.py <cmd> <input directory> <output directory>")
        sys.exit(0)

    if cmd == 'hierarchy':
        for filename in os.listdir(inputdir):
            hierarchize(inputdir, filename, outputdir)
    elif cmd == 'lang':
        for filename in os.listdir(inputdir):
            add_langs(inputdir, filename, outputdir)
    else:
        raise ValueError('Valid commands: hierarchy, lang. Usage: format_json.py <cmd> <input directory> <output directory>')