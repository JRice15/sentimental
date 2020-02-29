from flask import Flask, render_template, request, redirect
from datetime import datetime
import webbrowser
from urllib.parse import parse_qsl
import re
import get_sentiment as gs

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

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



def make_graph(post):
    """
    Make a sentiment graph from GUI info
    """
    # get the terms and subreddits
    terms = []
    subreddits = []
    for key, value in post.items():
        if value == "":
            value = None
        if key[:3] == "sub":
            subreddits.append(value)
        if key[:4] == "word":
            terms.append(value)
    
    queries = []
    for x in range(len(terms)):
        queries.append((terms[x],subreddits[x]))

    times = gs.convert_to_epoch(post)

    print(queries,times)
    gs.plot_sentiments_over_time(queries, times["end"], times["start"])



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

        make_graph(post)

    else:
        pass

    return render_template("index.html", post=Data.post, row_count=Data.row_count)


@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response


if __name__ == "__main__":
    app.run(debug=True)
    webbrowser.open_new("127.0.0.1:5000")

