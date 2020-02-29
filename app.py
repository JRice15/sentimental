from flask import Flask, render_template, request, redirect
from datetime import datetime
import webbrowser
from urllib.parse import parse_qsl
import re

app = Flask(__name__)


class Data:

    row_count = 1


@app.route("/", methods=['GET', 'POST'])
def root():
    post = None
    if request.method == "POST":
        post = request.get_data().decode("UTF-8")
        post = parse_qsl(post, keep_blank_values=True)
        post = {k:v for k,v in post}
        if post["submit-type"] == "clear":
            Data.row_count = 1
        elif post["submit-type"] == "add-row":
            Data.row_count += 1
        elif post["submit-type"] == "rm-row":
            Data.row_count = 1 if Data.row_count < 2 else Data.row_count - 1
    else:
        pass
    return render_template("index.html", data=post, row_count=Data.row_count)


if __name__ == "__main__":
    app.run(debug=True)
    webbrowser.open_new("127.0.0.1:5000")

