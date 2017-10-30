from flask import Flask, request
from flask_jsonpify import jsonify

import os
import time

app = Flask(__name__)

import matroid
from matroid.client import Matroid

api = Matroid(client_id = '8IcsUecnIM5sAhCu', client_secret = 'nqqk1XCUvQdzaowkzEcYgqOrTJT5z5F4')

@app.route('/')
def hello_world():
    detectors_to_use = api.list_detectors()
    print(detectors_to_use)
    return jsonify(detectors_to_use)

@app.route('/detector', methods=['GET', 'POST'])
def post():
    if request.method == 'GET':
        return '''
            <!DOCTYPE html>
                <title>Upload File</title>
                <form method="POST" enctype="multipart/form-data">
                      <input type="file" name="file">
                      <input type="submit" value="Upload">
                </form>
            </html>'''
    elif request.method == 'POST':
        file = request.files['file']
        print(file)
        filename = str(int(time.time()))+".jpeg"
        print(os.path.abspath(filename))
        file.save(filename)
        # Classifying a picture from a file path
        stadium_classification_result = api.classify_image(detector_id='5884afa19a7064289fb81cac', image_file=filename)
        print(stadium_classification_result)
        return jsonify(stadium_classification_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80', threaded=True)

