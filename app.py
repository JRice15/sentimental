from flask import Flask, render_template, request, redirect, config, send_from_directory
from datetime import datetime
import webbrowser
from urllib.parse import parse_qsl
import re
import get_sentiment as gs
import os
from data import Data

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1



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
        elif post["submit-type"] == "render":
            Data.update(post)
            make_graph(post)
        else:
            Data.update(post)

        i = 0
        while (i < len(Data.bins) - 1):
            if Data.bins[i] == Data.bins[i+1]:
                Data.bins.pop(i)
            i += 1
        Data.post["bins"] = Data.bins


    else:
        pass

    return render_template("index.html", post=Data.post, row_count=Data.row_count)


@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response



MEDIA_FOLDER = os.path.dirname(__file__)

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(MEDIA_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
    webbrowser.open_new("127.0.0.1:5000")

