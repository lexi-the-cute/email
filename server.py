from flask import Flask, request
from werkzeug.datastructures import MultiDict, CombinedMultiDict, ImmutableMultiDict, FileStorage

import bson
import json
import base64
import csv
import os

app = Flask(__name__)

def print_multi_dict(multidict: MultiDict):
    for key, value in multidict.items():
        print(f"{key} - {value}")

def store_multi_dict_as_bson(multidict: MultiDict):
    data: dict = {}

    for key, value in multidict.items():
        if type(value) == FileStorage:
            file: dict = {}
            file["filename"] = value.filename
            file["name"] = value.name
            file["content_type"] = value.content_type
            file["content_length"] = value.content_length
            file["body"] = value.stream.read()

            file["headers"] = []
            for hkey, hvalue in value.headers.items():
                file["headers"].append({hkey: hvalue})

            data[key] = file
        else:
            data[key] = value

    return bson.dumps(data)

def store_multi_dict_as_json(multidict: MultiDict):
    data: dict = {}

    for key, value in multidict.items():
        data[key] = value

    return json.dumps(data)

def log_email(output_file: str, message: str, attachments: bytes):
    create: bool = False
    if not os.path.exists(output_file):
        create: bool = True

    with open(output_file, mode="w") as f:
        writer = csv.writer(f)
        
        if create:
            writer.writerow(["message", "attachments"])
        
        writer.writerow([message, base64.b64encode(attachments).decode()])

@app.route('/webhook', methods=['POST'])
def webhook():
    values: CombinedMultiDict = request.values
    files: ImmutableMultiDict = request.files

    message: str = store_multi_dict_as_json(values)
    attachments: bytes = store_multi_dict_as_bson(files)

    log_email(output_file="emails.csv", message=message, attachments=attachments)

    return 'Received Email Webhook...'

@app.route('/notify', methods=['POST'])
def notify():
    values: CombinedMultiDict = request.values
    files: ImmutableMultiDict = request.files

    message: str = store_multi_dict_as_json(values)
    attachments: bytes = store_multi_dict_as_bson(files)

    log_email(output_file="notifications.csv", message=message, attachments=attachments)

    return 'Received Notification Webhook...'

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5001)