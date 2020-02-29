from flask import Flask, render_template, request, redirect
from datetime import datetime
import webbrowser
from urllib.parse import parse_qsl
import re

app = Flask(__name__)

class Data:

    post = {}
    row_count = 1

    @staticmethod
    def add_row(post):
        Data.post = post
        Data.row_count += 1

    @staticmethod
    def rm_row(post):
        if Data.row_count > 1:
            Data.row_count -= 1
            del [post["word{0}".format(Data.row_count)]]
            del [post["sub{0}".format(Data.row_count)]]
        Data.post = post

    @staticmethod
    def clear(post):
        Data.row_count = 1
        Data.post = {}

    @staticmethod
    def update(post):
        Data.post = post



@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == "POST":
        post = request.get_data().decode("UTF-8")
        post = parse_qsl(post, keep_blank_values=True)
        post = {k:v for k,v in post}

        if post["submit-type"] == "clear":
            Data.clear(post)
        elif post["submit-type"] == "add-row":
            Data.add_row(post)
        elif post["submit-type"] == "rm-row":
            Data.rm_row(post)
        else:
            Data.update(post)

    else:
        pass

    return render_template("index.html", post=Data.post, row_count=Data.row_count)


if __name__ == "__main__":
    app.run(debug=True)
    webbrowser.open_new("127.0.0.1:5000")

