from flask import Flask, render_template, request, redirect
from datetime import datetime
import webbrowser
from urllib.parse import parse_qsl
import re

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def root():
    data = None
    if request.method == 'POST':
        print(request.get_data())
        data = request.get_data().decode("UTF-8")
        data = parse_qsl(data, keep_blank_values=True)
        data = {k:v for k,v in data}
        print(data)
    else:
        pass
    return render_template("index.html", data=data)



if __name__ == "__main__":
    app.run(debug=True)
    webbrowser.open_new("127.0.0.1:5000")

