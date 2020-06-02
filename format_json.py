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
            form["serName" + str(i)]
            extra_services += 1
        # Break out if last service is reached
        except KeyError as e:
            break

    # Take the fields until the first service field
    common_fields = list(takewhile(lambda x: x != "serName", list(keys)))
    # Take the fields until first service field of second service (or end of file) and remove common fields
    service_fields = list(takewhile(lambda x: x != "serName0" and x != "end_notes", list(keys)))[len(common_fields):]

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

if __name__ == "__main__":
    import sys
    import os

    try:
        inputdir = sys.argv[1]
        outputdir = sys.argv[2]
    except IndexError:
        print("usage: format_json.py <input directory> <output directory>")
        sys.exit(0)

    for filename in os.listdir(inputdir):
        hierarchize(inputdir, filename, outputdir)
        