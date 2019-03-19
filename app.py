from flask import Flask, request, make_response, Response
import requests
from flask import render_template
import json
import os
import jwt
import json
import datetime
from functools import wraps
from DBConn import db

userDB = db.users

SECRET_KEY = b'-\x1c\x9b\xa7x\xacH\nE{\x85=\xa6\x0e[\xe2\xe3\xb2\x01D\xc4\xd2x\x0f'


# generates an encrypted auth token using the encrypted using the secret key valid for 24 hours
def encode_auth_token(userName):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=1),
            'iat': datetime.datetime.utcnow(),
            'username': userName
        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e


# Decodes the auth token and returns userid as integer if token is valid or else an error as a string
def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, SECRET_KEY)
        return 'SUCCESS' + payload['username']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


# Defines the @requires_auth decoration. Any endpoint with the decoration requires authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.cookies.get('sillyauth')
        if not auth_token:  # Authtoken no present so send 401
            res = make_response(render_template("login.html"))
            # res.set_cookie("sillyauth", value="I am cookie")
            return res
        user_name = decode_auth_token(auth_token)  # Get userid from authtoken
        if user_name.startswith('SUCCESS'):
            # set the userNameFromToken var so user can be identified form the request
            request.userNameFromToken = user_name[7:]
            # send control back to actual endpoint function
            return f(*args, **kwargs)
        else:
            res = make_response(render_template("login.html"))
            # res.set_cookie("sillyauth", value="I am cookie")
            return res

    return decorated


app = Flask(__name__)


@app.route("/")
@requires_auth
def hello():
    username = request.userNameFromToken
    print(username)
    try:
        record = userDB.find_one({'username': username})
        if record is None:
            return json.dumps({'message': "User doesn't exist.", 'success': False, 'code': 1})
        else:
            todos = record['todos'];
            res = make_response(render_template("home.html", todos=todos))
            return res
    except Exception as e:
        print(e)
        return json.dumps({'message': "Server error while checking if user exists.", 'code': 3})


@app.route("/login")
def lgin():
    res = make_response(render_template("login.html"))
    res.set_cookie("sillyauth", value="", expires=0)
    return res


@app.route("/auth", methods=['GET'])
def auth():
    username = request.args.get("username")
    try:
        record = userDB.find_one({'username': username})
        if record is None:
            return json.dumps({'message': "User doesn't exist.", 'success': False, 'code': 1})
        else:
            token = encode_auth_token(username).decode("utf-8")
            return json.dumps({'token': token})
    except Exception as e:
        print(e)
        return json.dumps({'message': "Server error while checking if user exists.", 'code': 3})


@app.route("/new", methods=['GET'])
def newUser():
    username = request.args.get("username")
    try:
        record = userDB.find_one({'username': username})
        if record is None:
            user = {'username': username, 'todos': []}
            result = userDB.insert_one(user)
            if result.inserted_id:
                print("created new user: " + username)
                return json.dumps({'success': True})
            else:
                return json.dumps({'message': "Server error while creating new user.", 'code': 7})
        else:
            return json.dumps({'message': "User already exists.", 'success': False, 'code': 1})
    except Exception as e:
        print(e)
        return json.dumps({'message': "Server error while checking if user exists.", 'code': 3})




@app.route("/newTodo", methods=['GET'])
@requires_auth
def new_todo():
    username = request.userNameFromToken
    content = request.args.get("username")

    try:
        record = userDB.find_one({'username': username})
        if record is None:
             return json.dumps({'message': "user not found.", 'code': 7})
        else:
            todos = record['todos']
            print(todos)
            exists = False
            for todo in todos:
                if todo['content'] == content:
                    exists = True
            if not exists:
                todos.append({'completed': False, 'content': content })
                result = userDB.update_one(
                    {"username": username},
                    {
                        "$set": {
                            "todos": todos,
                        }
                    }
                )
                if result.matched_count > 0:
                    return json.dumps({'success': True})
                else:
                    return json.dumps({'success': False, 'error': 'Adding todo failed for some reason', 'code': 998})
            return json.dumps({'success': False})
    except Exception as e:
        print(e)
        return json.dumps({'message': "Server error while checking if user exists.", 'code': 3})


@app.route("/completeItem", methods=['GET'])
@requires_auth
def complete():
    username = request.userNameFromToken
    content = request.args.get("id")

    try:
        record = userDB.find_one({'username': username})
        if record is None:
            return json.dumps({'message': "user not found.", 'code': 7})
        else:
            todos = record['todos']
            print(todos)
            exists = False
            for todo in todos:
                if todo['content'] == content:
                    exists = True
                    todo['completed'] = True
            if exists:
                result = userDB.update_one(
                    {"username": username},
                    {
                        "$set": {
                            "todos": todos,
                        }
                    }
                )
                if result.matched_count > 0:
                    return json.dumps({'success': True})
                else:
                    return json.dumps({'success': False, 'error': 'Completing todo failed for some reason', 'code': 998})
            return json.dumps({'success': False})
    except Exception as e:
        print(e)
        return json.dumps({'message': "Server error while checking if user exists.", 'code': 3})


@app.route("/uncompleteItem", methods=['GET'])
@requires_auth
def uncomplete():
    username = request.userNameFromToken
    content = request.args.get("id")

    try:
        record = userDB.find_one({'username': username})
        if record is None:
            return json.dumps({'message': "user not found.", 'code': 7})
        else:
            todos = record['todos']
            print(todos)
            exists = False
            for todo in todos:
                if todo['content'] == content:
                    exists = True
                    todo['completed'] = False
            if exists:
                result = userDB.update_one(
                    {"username": username},
                    {
                        "$set": {
                            "todos": todos,
                        }
                    }
                )
                if result.matched_count > 0:
                    return json.dumps({'success': True})
                else:
                    return json.dumps({'success': False, 'error': 'UnCompleting todo failed for some reason', 'code': 998})
            return json.dumps({'success': False})
    except Exception as e:
        print(e)
        return json.dumps({'message': "Server error while checking if user exists.", 'code': 3})


@app.route("/deleteItem", methods=['GET'])
@requires_auth
def deleteItem():
    username = request.userNameFromToken
    content = request.args.get("id")

    try:
        record = userDB.find_one({'username': username})
        if record is None:
            return json.dumps({'message': "user not found.", 'code': 7})
        else:
            todos = record['todos']
            print(todos)
            exists = False
            for todo in todos:
                if todo['content'] == content:
                    exists = True
                    todos.remove(todo)
            if exists:
                result = userDB.update_one(
                    {"username": username},
                    {
                        "$set": {
                            "todos": todos,
                        }
                    }
                )
                if result.matched_count > 0:
                    return json.dumps({'success': True})
                else:
                    return json.dumps({'success': False, 'error': 'Deleting todo failed for some reason', 'code': 998})
            return json.dumps({'success': False})
    except Exception as e:
        print(e)
        return json.dumps({'message': "Server error while checking if user exists.", 'code': 3})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
