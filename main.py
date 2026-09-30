from venv import create

from flask import Flask, redirect, url_for,render_template

app = Flask(__name__)

@app.route("/") #default domain route demek
def Home():
    return render_template("home.html")

@app.route("/Kampanyalar/")
def Campaign():
    Sayfad="Kampanya Sayfası"
    return Sayfad

@app.route("/Search/")
def Search():
    search="Search for campaign"
    return search

@app.route("/create/")
def Create():
    create="Create a campaign"
    return create

if __name__ == '__main__':
    app.run(debug=True)
