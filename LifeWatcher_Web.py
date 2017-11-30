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

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
API_SERVICE_NAME = 'drive'
SCOPES=[
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
      ]
API_VERSION = 'v2'

app = Flask(__name__)

# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
#760668503313-1024oeh105l8te3voorffd3ckuk691jo.apps.googleusercontent.com
#rOidowp9-T5dXR2J8DM5536j
app.secret_key = 'rOidowp9-T5dXR2J8DM5536j'

from matroid.client import Matroid
# Zhen
# api = Matroid(client_id = '8IcsUecnIM5sAhCu', client_secret = 'nqqk1XCUvQdzaowkzEcYgqOrTJT5z5F4')
# Hao
api = Matroid(client_id='CiAqy5iYxjsbwcZx', client_secret='raI42Xl0w4tAo1CCjnPICBzLYpeEyozW')


# get a detector by user id and detector name
def get_a_detector(user_id, detector_name):
    client = get_an_instance()
    target_detector = client.local.users.find({'user_id': user_id, 'detector_name': detector_name})
    client.close()
    return target_detector['detector_id']


# get a detector id by camera id
def get_detector_by_camera(user_id, camera_id):
    client = get_an_instance()
    target = client.local.cameras.find_one(
        {
            'user_id': user_id,
            'camera_id': camera_id
        }
    )
    if target:
        return target['detector_id']
    else:
        return None


def get_keyword(detector_id):
    client = get_an_instance()
    target = client.local.detectors.find_one({'id': detector_id})
    client.close()
    return target['name']


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


# Save the path of an image from a camera to database
def insert_image(user_id, camera_id, image_path):
    client = get_an_instance()
    exist = client.local.monitor.find_one({
        'user_id': user_id,
        'camera_id': camera_id
    })
    if exist:
        try:
            client.local.monitor.update_one(
                {
                    "user_id": user_id,
                    "camera_id": camera_id,
                },
                {
                    '$set': {'image_path': image_path}
                }
            )
            client.close()
            return True
        except Exception:
            return False
    else:
        try:
            client.local.monitor.insert_one(
                {
                    "user_id": user_id,
                    "camera_id": camera_id,
                    'image_path': image_path
                }
            )
            client.close()
            return True
        except Exception:
            client.close()
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
    api.train_detector(detector_id)
    if insert_detector(keyword, detector_id, zip_file):
        print("Detector is created and saved.")
    else:
        return "Saving detector failed."
    return detector_id


# Search images
def search_images(keyword):
    base_path = '/Downloads/' # /Users/Ethan
    file_path = base_path + 'images/' + keyword
    folder_path = base_path + keyword
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
        result = detector_id['detector_name']
        client.close()
        return result
    client.close()
    return result


# List all cameras of a user
def list_all_cameras(user_id):
    client = get_an_instance()
    result = client.local.cameras.find({'user_id': user_id})
    c_list = []
    for c in result:
        c_list.append(c['camera_id'])
    return c_list


@app.route('/')
def hello():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    # return redirect('http://localhost:5000/index.html')
    return redirect("http://ec2-18-216-37-90.us-east-2.compute.amazonaws.com/index.html", code=302)


@app.route('/<path:path>')
def static_file(path):
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
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


# Deprecated. List available detectors
def list_detectors():
    # detectors_to_use = api.list_detectors()
    user_id = flask.session['email_address']
    client = get_an_instance()
    detectors_available = client.local.users.find({'user_id': user_id})
    client.close()
    return detectors_available['detector_name'], detectors_available['detector_id']


@app.route('/rest/api/detector', methods=['GET', 'POST'])
def detector_creation():
    if request.method == 'GET':
        user_id = flask.session['email_address']
        client = get_an_instance()
        detectors_available = client.local.users.find({'user_id': user_id})
        client.close()
        detectors = []
        for d in detectors_available:
            content = {'name': d['detector_name'], 'id': d['detector_id']}
            detectors.append(content)
        return jsonify({'detectors': detectors})
    # Need a keyword here to search
    keyword = request.values['keyword']
    name = request.values['detector_name']
    user_id = flask.session['email_address']
    detector_id = detector_factory(user_id=user_id, keyword=keyword, detector_name=name)
    api.train_detector(detector_id)
    detector_info = api.detector_info(detector_id)
    while detector_info['detector']['state'] == 'pending':
        api.train_detector(detector_id)
        detector_info = api.detector_info(detector_id)
    return jsonify({'detector id': detector_id, 'detector info': detector_info})


@app.route('/rest/api/camera/setting', methods=['GET', 'POST'])
def alert_setting():
    user_id = flask.session['email_address']
    camera_id = request.form['camera_id']
    detector_name = request.form['detector_name']
    status = 42
    description = 'Setting failed.'
    detector_info = bind_camera_detector(user_id=user_id, camera_id=camera_id, detector_name=detector_name)
    if detector_info:
        status = 0
        description = 'Setting completed.'

    # setting = {
    #     'camera_id': 12315,
    #     'condition': {
    #         'detector_id': 12345678901,
    #         'human_name': "Bear",
    #         'positive': False  # also could be True, means if then or if not then
    #         }
    # }

    result = {
        'results': {
            'status': status,  # 0 is success, the others could be fault, reason in description
            'description': description,
            'camera_id': camera_id,
            'detector': detector_info
        }
    }
    return jsonify(result)


@app.route('/rest/api/camera', methods=['GET'])  # , 'POST'
def camera_list():
    user_id = flask.session['email_address']
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


# Deprecated. Has been integrated to alert_setting
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
                    "name": "0"
                  },
                  "predictions": [
                    {
                      "labels": {
                        "American Black Bear": 0
                      }
                    }
                  ]
                }
              ]
        }
        file = request.files['file']
        user_id = request.values['email']  # email
        camera_id = request.values['uuid']  # uuid

        detector_id = get_detector_by_camera(user_id, camera_id)
        if not detector_id:
            response = flask.Response(json.dumps(result))
            response.headers['Access-Control-Allow-Origin'] = '*'  # This is important for Mobile Device
            return response
        keyword = get_keyword(detector_id)
        # print(file, email, uuid)
        base_folder = 'monitor/' + user_id + '/' + camera_id + '/'  # /Users/Ethan/Downloads/
        filename = 'monitor.jpeg'  # str(int(time.time())) + ".jpeg"
        alert_filename = 'alert_monitor.jpeg'
        fullname = base_folder + filename
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
        file.save(fullname)
        # print(os.path.abspath(filename))

        # Classifying a picture from a file path
        classification_result = api.classify_image(detector_id=detector_id, image_file=fullname)
        # print(stadium_classification_result)
        # print(classification_result)
        value = classification_result['results'][0]['predictions'][0]['labels'][keyword]
        if value > 0.5:
            filename = 'alert_monitor.jpeg'
        elif os.path.isfile(base_folder + alert_filename):
            os.remove(base_folder + alert_filename)
        fullname = base_folder + filename
        file.save(fullname)
        insert_image(user_id, camera_id, fullname)

        response = flask.Response(json.dumps(classification_result))
        response.headers['Access-Control-Allow-Origin'] = '*'  #This is important for Mobile Device
        return response


@app.route('/rest/api/check', methods=['POST'])
def check():
    user_id = flask.session['email_address']
    camera_id = request.values['camera_id']
    image_path = 'monitor/' + user_id + '/' + camera_id + '/alert_monitor.jpeg'
    if os.path.isfile(image_path):
        return image_path
    return 'Error: no image found.'


# #################COPY GOOGLE AUTH SAMPLE
@app.route('/test')
def test_api_request():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  drive = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  files = drive.files().list().execute()

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.jsonify(**files)


@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():

    # Specify the state when creating the flow in the callback so that it can
    #  verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
          CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    user = flow.oauth2session.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
    flask.session['email_address'] = user['email']
    print(user)

    return flask.redirect(flask.url_for('hello'))

# user = User.filter_by(google_id=userinfo['id']).first()
#     if user:
#         user.name = userinfo['name']
#         user.avatar = userinfo['picture']
#     else:
#         user = User(google_id=userinfo['id'],
#                     name=userinfo['name'],
#                     avatar=userinfo['picture'])
#     db.session.add(user)
#     db.session.flush()
#     login_user(user)
#     return redirect(url_for('index'))


@app.route('/logout')
def logout():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    clear_credentials()
    return flask.redirect(flask.url_for('hello'))
    # return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.route('/logout')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return flask.redirect(flask.url_for('hello'))
  # return ('Credentials have been cleared.<br><br>' +
  #         print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(threaded=True)
# host='0.0.0.0', port='80',
