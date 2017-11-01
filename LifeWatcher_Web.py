from flask import Flask, request, redirect
from flask_jsonpify import jsonify

import os
import time
import flask
import json
app = Flask(__name__)

from matroid.client import Matroid

api = Matroid(client_id = '8IcsUecnIM5sAhCu', client_secret = 'nqqk1XCUvQdzaowkzEcYgqOrTJT5z5F4')

@app.route('/')
def hello():
    return redirect("http://ec2-18-216-37-90.us-east-2.compute.amazonaws.com/api", code=302)

@app.route('/api')
def api_list():
    # detectors_to_use = api.list_detectors()
    # print(detectors_to_use)
    # response = flask.Response(str(detectors_to_use))
    # response.headers['Access-Control-Allow-Origin'] = '*'
    body = '''
            <!DOCTYPE html>
                <h1>Life Watcher REST API
                <p>
                create detector: <a href="/rest/api/detector">/rest/api/create</a>
                <p>
                alert condition: <a href="/rest/api/username/camera/12306/setting">/rest/api/user/camera/id/setting</a>
                <p>
                get camera list: <a href="/rest/api/username/camera">/rest/api/user/camera</a>
                <p>
                do a detection: <a href="/rest/api/detection">/rest/api/detection</a>
            </html>'''
    response = flask.Response(body)
    return response

@app.route('/rest/api/detector', methods=['GET', 'POST'])
def detector_creation():
    result = {
        'results': {
            'status':0,#0 is success, the others could be fault, reason in description
            'description':'Create Success.',
            'detector': {
                'detector_id':12345678901,
                'human_name':"Bear",
                'label':['Bear','Panda'],
                'permission_level':'private'# also could be open, see matroid
            }
        }
    }
    return jsonify(result)

@app.route('/rest/api/<string:username>/camera/<int:id>/setting', methods=['GET', 'POST'])
def alert_setting(username, id):
    setting = {
        'camera_id': 12315,
        'condition': {
            'detector_id': 12345678901,
            'human_name': "Bear",
            'positive': False  # also could be True, means if then or if not then
            }
    }

    result = {
        'results': {
            'status': 0,  # 0 is success, the others could be fault, reason in description
            'description': 'Setting Success.',
            'camera_id':12315,
            'condition': {
                'detector_id': 12345678901,
                'human_name': "Bear",
                'label': ['Bear', 'Panda'],
                'permission_level': 'private',  # also could be open, see matroid
                'positive': True  # also could be False, means if then or if not then
            }
        }
    }

    result['setting'] = setting
    return jsonify(result)

@app.route('/rest/api/<string:username>/camera', methods=['GET', 'POST'])
def camera_list(username):
    result = {
        'results': {
            'status': 0,  # 0 is success, the others could be fault, reason in description
            'description': 'Setting Success.',
            'lists':[ {
                    'camera_id': 12306,
                    'state': {
                        'online': True,  # True is online, the others could be offline, reason in description
                        'description': 'Online in detection',
                        'camera_id': 1234,
                        'condition': {
                            'detector_id': 12345678901,
                            'human_name': "Bear",
                            'label': ['Bear', 'Panda'],
                            'permission_level': 'private',  # also could be open, see matroid
                            'positive': True  # also could be False, means if then or if not then
                        }
                    }
                }, {
                    'camera_id': 12315,
                    'results': {
                        'online': False,  # True is online, the others could be offline, reason in description
                        'description': 'offline the detection',
                        'camera_id': 1234,
                        'condition': {
                            'detector_id': 12345678901,
                            'human_name': "Bear",
                            'label': ['Bear', 'Panda'],
                            'permission_level': 'private',  # also could be open, see matroid
                            'positive': True  # also could be False, means if then or if not then
                        }
                    }
                }
            ]
        }
    }
    return jsonify(result)

@app.route('/rest/api/detection', methods=['GET', 'POST'])
def detector():
    if request.method == 'GET':
        body = '''
            <!DOCTYPE html>
                <title>Upload File</title>
                <h1>Life Watcher REST API
                <p>
                <form method="POST" enctype="multipart/form-data">
                      <input type="file" name="file">
                      <input type="submit" value="Upload">
                </form>
            </html>'''
        response = flask.Response(body)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    elif request.method == 'POST':
        result = {
              "results": [
                {
                  "file": {
                    "name": "1509446116.jpeg"
                  },
                  "predictions": [
                    {
                      "labels": {
                        "American Black Bear": 0.9384055137634277
                      }
                    }
                  ]
                }
              ]
        }
        file = request.files['file']
        print(file)
        filename = str(int(time.time()))+".jpeg"
        print(os.path.abspath(filename))
        file.save(filename)
        # Classifying a picture from a file path
        stadium_classification_result = api.classify_image(detector_id='5884afa19a7064289fb81cac', image_file=filename)
        print(stadium_classification_result)
        response = flask.Response(json.dumps(stadium_classification_result))
        response.headers['Access-Control-Allow-Origin'] = '*' #This is important for Mobile Device
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80', threaded=True)

