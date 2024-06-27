from flask import Flask, request, redirect
import datetime
from replit import db
import os
from groq import Groq


app = Flask(__name__, static_url_path='/static')
Yeid = os.environ['Yeid']
client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)



def getChat(isAdmin):
  message = ""
  f = open("template/message.html", "r")
  message = f.read()
  f.close()
  keys = db.keys()
  keys = list(keys)
  result = ""
  recent = 0
  for key in keys:
    myMessage = message
    myMessage = myMessage.replace("{username}", db[key]["username"])
    myMessage = myMessage.replace("{timestamp}", key)
    myMessage = myMessage.replace("{message}", db[key]["urmessage"])
    
    myMessage = myMessage.replace("{answer}", db[key]["Airesponse"])


    if isAdmin == Yeid:
      myMessage = myMessage.replace("{admin}", f"""<a href="/delete?id={key}"><img src="/static/images/delete.png" style="width: 15px; height: 15px;"> </a>""")
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
  urmessage = form["message"]
  date = datetime.datetime.now()
  timestamp = datetime.datetime.timestamp(date)
  prompt = (f"Answer the {urmessage} like wizard, but be as short as possible. Answer in the same language the user is using. Your answer must be under 50 words")
  response = client.chat.completions.create(
      messages=[
          {
              "role": "user",
              "content": prompt,
          }
      ],
      model="llama3-8b-8192",
  )

  Airesponse = response.choices[0].message.content
  userid = request.headers["X-Replit-User-Id"]
  username = request.headers["X-Replit-User-Name"]
  db[datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = {
    "username": username,
    "urmessage": request.form['message'],
    "Airesponse" : Airesponse
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
