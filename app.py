from flask import Flask, render_template, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import webbrowser

app = Flask(__name__)





@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        pass
    else:
        pass
    obj = BasicObj("test1")
    return render_template("index.html", obj=obj)



if __name__ == "__main__":
    app.run(debug=True)
    webbrowser.open_new("127.0.0.1:5000")

