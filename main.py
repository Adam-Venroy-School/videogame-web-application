from flask import render_template
from database import *

app.secret_key = 'supersecretkey'

@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
