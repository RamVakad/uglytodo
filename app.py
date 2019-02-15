from flask import Flask, request, make_response
import requests
from flask import render_template
import json
import os

app = Flask(__name__)

@app.route("/")
def hello():
  if ('sillyauth' in request.cookies):
    sillyauth = request.cookies.get('sillyauth')
    print(sillyauth)
    r = requests.get('https://hunter-todo-api.herokuapp.com/todo-item', cookies=request.cookies)
    if (r.status_code == 200):
      jsonified = json.loads(r.text)
      print(jsonified)
      todos = jsonified
      res = make_response(render_template("home.html", todos=todos))

    #res.set_cookie("sillyauth", value="", expires=0)
    return res
  else:
    res = make_response(render_template("login.html"))
    #res.set_cookie("sillyauth", value="I am cookie")
    return res

@app.route("/login")
def lgin():
    res = make_response(render_template("login.html"))
    res.set_cookie("sillyauth", value="", expires=0)
    return res

@app.route("/auth", methods = ['GET'])
def auth():
  username = request.args.get("username")
  #print(username)
  r = requests.post('https://hunter-todo-api.herokuapp.com/auth', json = {'username': username})
  if (r.status_code == 200):
    jsonified = json.loads(r.text)
    print(jsonified)
    return json.dumps(jsonified)
  else:
    return json.dumps({ 'message': 'User does not exist or sever error.' })

@app.route("/new", methods = ['GET'])
def newuser():
  username = request.args.get("username")
  #print(username)
  r = requests.post('https://hunter-todo-api.herokuapp.com/user', json = {'username': username})
  if (r.status_code == 201):
    jsonified = json.loads(r.text)
    print(jsonified)
    return json.dumps(jsonified)
  else:
    return json.dumps({ 'message': 'fail create user' })

@app.route("/newTodo", methods = ['GET'])
def newTodo():
  username = request.args.get("username")
  #print(username)
  r = requests.post('https://hunter-todo-api.herokuapp.com/todo-item', json = {'content': username}, cookies=request.cookies)
  print(r.text)
  if (r.status_code == 201):
    jsonified = json.loads(r.text)
    print(jsonified)
    return json.dumps({'success': True})
  else:
    return json.dumps({ 'message': 'fail create user' })

@app.route("/completeItem", methods = ['GET'])
def complete():
  id = request.args.get("id")
  r = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/'+id, json = {'completed': True}, cookies=request.cookies)
  print(r.text)
  if (r.status_code == 200):
    jsonified = json.loads(r.text)
    print(jsonified)
    return json.dumps({'success': True})
  else:
    return json.dumps({ 'message': 'fail create user' })

@app.route("/uncompleteItem", methods = ['GET'])
def uncomplete():
  id = request.args.get("id")
  r = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/'+id, json = {'completed': False}, cookies=request.cookies)
  print(r.text)
  if (r.status_code == 200):
    jsonified = json.loads(r.text)
    print(jsonified)
    return json.dumps({'success': True})
  else:
    return json.dumps({ 'message': 'fail create user' })

@app.route("/deleteItem", methods = ['GET'])
def deleteItem():
  id = request.args.get("id")
  r = requests.delete('https://hunter-todo-api.herokuapp.com/todo-item/'+id, cookies=request.cookies)
  print(r.status_code)
  if (r.status_code == 204):
    return json.dumps({'success': True})
  else:
    return json.dumps({ 'message': 'fail create user' })


if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, threaded=True)