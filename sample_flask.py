import flask
from flask import *

app = Flask(__name__)

@app.route("/username/<name>")
def index(name):
    return "<h1>Hello {}</h1>".format(name)

if __name__=='__main__':
    app.run(debug=True)


