import json


if __name__ == "__main__":
    with open('testforms/old_infra.json', encoding='utf-8') as f:
        forms = json.load(f)
    
    for idx, form in enumerate(forms):
        with open('old_infras/' + str(idx) + '.json', 'w+', encoding='utf-8') as f:
            f.write(json.dumps(form, ensure_ascii=False, indent=4).encode('utf-8').decode())