from flask import Flask, request, redirect
import datetime
from replit import db
import os

app = Flask(__name__, static_url_path='/static')
Yeid = os.environ['Yeid']


def getChat(isAdmin):
  message = ""
  f = open("template/message.html", "r")
  message = f.read()
  f.close()
  keys = db.keys()
  keys = list(keys)
  result = ""
  recent = 0
  for key in reversed(keys):
    myMessage = message
    myMessage = myMessage.replace("{username}", db[key]["username"])
    myMessage = myMessage.replace("{timestamp}", key)
    myMessage = myMessage.replace("{message}", db[key]["message"])

    if isAdmin == Yeid:
      myMessage = myMessage.replace("{admin}", f"""<a href="/delete?id={key}"> ❌</a>""")
    else:
      myMessage = myMessage.replace("{admin}", "")

    result += myMessage
    recent += 1
    if recent == 5:
      break
  return result


@app.route('/')
def index():
  page = ""
  f = open("template/chat.html", "r")
  page = f.read()
  f.close()
  page = page.replace("{username}", request.headers["X-Replit-User-Name"])
  page = page.replace("{chats}", getChat(request.headers["X-Replit-User-Id"]))
  return page

@app.route('/add', methods=["POST"])
def add():
  form = request.form
  message = form["message"]
  date = datetime.datetime.now()
  timestamp = datetime.datetime.timestamp(date)
  userid = request.headers["X-Replit-User-Id"]
  username = request.headers["X-Replit-User-Name"]
  db[datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = {
    "username": username,
    "message": request.form['message']
  }
  print(userid)
  #page = f"""{userid} {username} {timestamp} {message}"""
  return redirect("/")


@app.route('/delete', methods=["GET"])
def delete():
  if request.headers["X-Replit-User-Id"] != Yeid:
    return redirect("/")
  results = request.values["id"]
  del db[results]
  return redirect("/")


if __name__ == '__main__':
  app.run(debug=True)
  app.run(host='0.0.0.0', port=81)
