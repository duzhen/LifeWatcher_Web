from flask import Flask, request, redirect
from flask_jsonpify import jsonify
from pymongo import mongo_client

import os
import time
import flask
import httplib2
import json
import shutil
import requests
app = Flask(__name__)

from matroid.client import Matroid
# Zhen
# api = Matroid(client_id = '8IcsUecnIM5sAhCu', client_secret = 'nqqk1XCUvQdzaowkzEcYgqOrTJT5z5F4')
# Hao
api = Matroid(client_id='CiAqy5iYxjsbwcZx', client_secret='raI42Xl0w4tAo1CCjnPICBzLYpeEyozW')


# List available detectors
def list_detectors(user_id):
    # detectors_to_use = api.list_detectors()
    client = get_an_instance()
    detectors_available = client.local.users.find({'user_id': user_id})
    client.close()
    return detectors_available['detector_name'], detectors_available['detector_id']


def get_a_detector(user_id, detector_name):
    client = get_an_instance()
    target_detector = client.local.users.find({'user_id': user_id, 'detector_name': detector_name})
    client.close()
    return target_detector['detector_id']


# Classifying a picture from a file path
def classify_image_file():
    image_classification_result = api.classify_image(detector_id='59f93660973ab10187c7d8df', image_file='one.jpg')
    return image_classification_result


# Get a database client instance
def get_an_instance():
    client = None
    try:
        client = mongo_client.MongoClient("mongodb://localhost:27017")
    except Exception:
        print("Database connection error.")
    return client


# Check if the keyword is already in the database
def exist_in_database(keyword):
    client = get_an_instance()
    result = client.local.detectors.find_one({'name': keyword})
    client.close()
    return result


# Insert the detector to database with the path of zip file
def insert_detector(keyword, detector_id, zip_file):
    client = get_an_instance()
    try:
        client.local.detectors.insert_one(
            {
                "name": keyword,
                "id": detector_id,
                "zip": zip_file
            }
        )
        client.close()
        return True
    except Exception:
        return False


# Bind the detector to a user
def bind_detector_user(user_id, detector_name, detector_id):
    client = get_an_instance()
    try:
        client.local.users.insert_one(
            {
                "user_id": user_id,
                "detector_name": detector_name,
                "detector_id": detector_id,
                "cameras": [],
                "status": "active"
            }
        )
        client.close()
        return True
    except Exception:
        return False


# Function for detector creation
def detector_factory(user_id, keyword, detector_name):
    detector_data = exist_in_database(keyword)
    if detector_data is None:
        detector_data = dict(id='')
        detector_data['id'] = create_a_detector(keyword=keyword, detector_name=detector_name)
    # Bind the detector to the user
    if bind_detector_user(user_id, detector_name, detector_data['id']):
        print("Binding completed.")
    else:
        return "Binding failed."
    return detector_data['id']


# Create and train a detector
def create_a_detector(keyword, detector_name):
    zip_file = search_images(keyword=keyword)
    # print(zip_file)
    detector_id = api.create_detector(zip_file=zip_file, name=detector_name, detector_type='general')['detector_id']
    # api.train_detector(detector_id)
    if insert_detector(keyword, detector_id, zip_file):
        print("Detector is created and saved.")
    else:
        return "Saving detector failed."
    return detector_id


# Search images
def search_images(keyword):
    base_path = '/Downloads/'
    file_path = base_path + 'images/' + keyword
    folder_path = '/Downloads/' + keyword
    headers = {'Content-Type': 'application/json'}
    http = httplib2.Http()
    api_key = 'AIzaSyBhK_WOCFeEJ--ew76gFdlbtnqgQqrbkE0'
    engine_id = '013117329555914261701:pwgtbqdu4zy'
    api_url = 'https://www.googleapis.com/customsearch/v1?key=' + api_key + '&searchType=image&cx=' + engine_id + '&q=' + keyword

    response, content = http.request(api_url, "GET", headers=headers)

    result = json.loads(content.decode())
    items = result['items']
    if download_images(items=items, folder=folder_path):
        # compress the images
        shutil.make_archive(file_path, 'zip', root_dir=base_path, base_dir=keyword)

    else:
        return 'Error'
    return file_path + '.zip'


# Download all images
def download_images(items, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for item in items:
        link = item['link']
        file_name = folder + '/' + link.split('/')[-1]

        r = requests.get(item['link'], stream=True)
        if r.status_code == 200:
            with open(file_name, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    return True


# Bind a camera to a detector
def bind_camera_detector(user_id, camera_id, detector_name):
    client = get_an_instance()
    result = None
    detector_id = client.local.users.find_one(
        {'user_id': user_id, 'detector_name': detector_name}
    )
    if detector_id:
        result = client.local.cameras.find_one(
            {
                "user_id": user_id,
                "camera_id": camera_id
            })
        if result:
            client.local.cameras.update_one(
                {
                    'user_id': user_id,
                    'camera_id': camera_id
                },
                {'$set': {'detector_id': detector_id['detector_id']}})
        else:
            client.local.cameras.insert_one(
                {'user_id': user_id,
                 'camera_id': camera_id,
                 'detector_id': detector_id['detector_id']}
            )
        client.close()
        return 'Success'
    client.close()
    return 'Detector not found'


# List all cameras of a user
def list_all_cameras(user_id):
    client = get_an_instance()
    result = client.local.cameras.find({'user_id': user_id})
    return result


@app.route('/')
def hello():
    return redirect("http://ec2-18-216-37-90.us-east-2.compute.amazonaws.com/api", code=302)


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


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
    # Need a keyword here to search
    keyword = 'mustang' # request.form['keyword']
    name = 'big_boat'
    user_id = 'u001'
    detector_id = detector_factory(user_id=user_id, keyword=keyword, detector_name=name)
    api.train_detector(detector_id)
    detector_info = api.detector_info(detector_id)
    return jsonify({'detector id': detector_id, 'detector info': detector_info})


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
def camera_list():
    user_id = ''
    result = list_all_cameras(user_id)
    # result = {
    #     'results': {
    #         'status': 0,  # 0 is success, the others could be fault, reason in description
    #         'description': 'Success.',
    #         'lists':[ {
    #                 'camera_id': 12306,
    #                 'state': {
    #                     'online': True,  # True is online, the others could be offline, reason in description
    #                     'description': 'Online in detection',
    #                     'camera_id': 1234,
    #                     'condition': {
    #                         'detector_id': 12345678901,
    #                         'human_name': "Bear",
    #                         'label': ['Bear', 'Panda'],
    #                         'permission_level': 'private',  # also could be open, see matroid
    #                         'positive': True  # also could be False, means if then or if not then
    #                     }
    #                 }
    #             }, {
    #                 'camera_id': 12315,
    #                 'results': {
    #                     'online': False,  # True is online, the others could be offline, reason in description
    #                     'description': 'offline the detection',
    #                     'camera_id': 1234,
    #                     'condition': {
    #                         'detector_id': 12345678901,
    #                         'human_name': "Bear",
    #                         'label': ['Bear', 'Panda'],
    #                         'permission_level': 'private',  # also could be open, see matroid
    #                         'positive': True  # also could be False, means if then or if not then
    #                     }
    #                 }
    #             }
    #         ]
    #     }
    # }
    return jsonify(result)


@app.route('/rest/api/bind_camera', methods=['GET', 'POST'])
def bind_camera():
    user_id = 'u001'
    camera_id = 'c005'
    detector_name = 'big_boat'
    if bind_camera_detector(user_id=user_id, camera_id=camera_id, detector_name=detector_name):
        return 'Success'
    return 'Failure'


@app.route('/rest/api/release_camera', methods=['POST'])
def release_camera():
    user_id = 'u001'
    camera_id = ['c002', 'c005']
    client = get_an_instance()
    client.local.cameras.find_one_and_update({'user_id': user_id, 'camera_id': camera_id},
                                             {'$set': {'detector_id': ''}})
    client.close()


@app.route('/rest/api/register', methods=['POST'])
def create_user():
    user_id = 'u001'
    password = '123'
    client = get_an_instance()
    try:
        client.local.credentials.insert_one(
            {
                "user_id": user_id,
                "password": password
            }
        )
        client.close()
        return 'Register completed.'
    except Exception:
        client.close()
        return 'Register failed!'


@app.route('/rest/api/detection', methods=['GET', 'POST'])
def detector():
    if request.method == 'GET':
        body = '''
            <!DOCTYPE html>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
                <title>Upload File</title>
                <h1>Life Watcher REST API Demo
                <p>
                <form method="POST" enctype="multipart/form-data">
                      <input type="file" id="imgInp" name="file">
                      <input type="submit" value="Upload">
                </form>
                <p>
                <img id="blah" src="#" alt="" height="50%" width="50%"/>
                <script>
                    function readURL(input) {

                    if (input.files && input.files[0]) {
                        var reader = new FileReader();
                    
                        reader.onload = function(e) {
                          $('#blah').attr('src', e.target.result);
                        }
                    
                        reader.readAsDataURL(input.files[0]);
                      }
                    }
                    
                    $("#imgInp").change(function() {
                      readURL(this);
                    });
                </script>
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
        email = request.values['email']
        uuid = request.values['uuid']
        print(file, email, uuid)
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
    app.run(host='0.0.0.0', port='80',threaded=True)
# host='0.0.0.0', port='80',
