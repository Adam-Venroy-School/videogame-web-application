from flask import render_template, redirect, url_for
from database import *

app.secret_key = 'supersecretkey'

@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
def home():
    return render_template('home.html')

#If anything other than home is reached, it will be redirected to home page
@app.errorhandler(404)
def error(e):
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
