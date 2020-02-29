from flask import Flask, render_template, request, redirect
from datetime import datetime
import webbrowser

app = Flask(__name__)



@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        print(request.get_data())
        print(request.get_json())
    else:
        pass
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
    webbrowser.open_new("127.0.0.1:5000")

