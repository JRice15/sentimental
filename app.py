from flask import Flask, render_template, request, redirect, config, send_from_directory, jsonify
from datetime import datetime
import webbrowser
from urllib.parse import parse_qsl
import re
import get_sentiment as gs
import os
from data import Data
from collections import OrderedDict
import time

import queue
from multiprocessing import Queue, Process, get_context

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1



def make_graph(post, q):
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

    gs.plot_sentiments_over_time(queries, times["end"], times["start"], q)



@app.route('/_check_render')
def check_render():
    print("check render")
    try:
        item = Data.q.get(False)
        Data.complete_queries += 1
        if item == "_bins":
            while True:
                try:
                    item = Data.q.get(False)
                    Data.bins = list(OrderedDict.fromkeys(item))
                    return jsonify(False, Data.complete_queries, Data.num_queries)
                except queue.Empty:
                    time.sleep(0.1)
        if item == "_done":
            Data.p.join()
            Data.p.terminate()
        print(" ", item)
        return jsonify(True, Data.complete_queries, Data.num_queries, item)
    except queue.Empty:
        print("  no result")
        return jsonify(False, Data.complete_queries, Data.num_queries)


def render(post):
    Data.update(post)
    Data.complete_queries = 0
    ctx = get_context('spawn')
    Data.q = ctx.Queue()
    Data.p = ctx.Process(target=make_graph, args=(post, Data.q))
    Data.p.start()


@app.route("/", methods=['GET', 'POST'])
def root():
    rendering = False

    if request.method == "POST":
        post = request.get_data().decode("UTF-8")
        post = parse_qsl(post, keep_blank_values=True)
        post = {k:v for k,v in post}

        Data.num_queries = 0
        i = 0
        while ("word" + str(i) in post) or ("sub" + str(i) in post):
            Data.num_queries += 1
            i += 1

        if (Data.p is not None):
            if (Data.p.is_alive):
                print("killing")
                try:
                    Data.p.terminate()
                except Exception as e:
                    print(e)
        if "submit-type" not in post:
            post["submit-type"] = "update"
        if post["submit-type"] == "clear":
            Data.clear(post)
        elif post["submit-type"] == "add-row":
            Data.add_row(post)
        elif post["submit-type"] == "rm-row":
            Data.rm_row(post)
        elif post["submit-type"] == "render":
            rendering = True
            render(post)
        else:
            Data.update(post)
    

        Data.post["bins"] = Data.bins


    return render_template("index.html", 
        post=Data.post, row_count=Data.row_count, request=request, 
        rendering=rendering)



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

