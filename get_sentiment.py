#Getting JSON from webpage
#!/usr/bin/env python
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
import json

import re

from textblob import TextBlob

import matplotlib.pyplot as plt

import matplotlib.dates as mdate


# Thank you Martin Thoma from stack overflow for this function
def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def pushshift_comment(q = None, ids = None, size = None, fields = None, sort = None, 
    sort_type = None, aggs = None, author = None, subreddit = None, after = None, before = None, 
    frequency = None, metadata = None):
    """
    Returns a dictionary of the data returned from the pushift request 
    
    Input:
        q - Search term. (String)
        ids - Get specific comments via their ids (list of base36 ids)
        size - Number of search terms to return (0 < int < 501)
        fields - Which fields to return (list of strings)
        sort - Sort results in a specific order ("asc", "desc")
        sort_type - Sort by a specific attribute ("score", "num_comments", "created_utc")
        aggs - Return aggregation summary ("author", "link_id", "created_utc", "subreddit")
        author - Limit to specific author (string)
        subreddit - Limit to specific subreddit (string)
        after - Search after this time (int of epoch value or Integer + "s,m,h,d" (i.e. 30d for 30 days))
        before - Search before this time (int of epoch value or Integer + "s,m,h,d" (i.e. 30d for 30 days))
        frequency - Used with the aggs parameter when set to created_utc ("second", "minute", "hour", "day")
        metadata - display metadata about the query (bool)

    Output:
        dict - a dictionary of comments/info
    
    Thank you to Jason Baumgartner who hosts and maintains pushshift
    https://github.com/pushshift/api
    """
    # Make one giant dictonary for east formatting
    args = {"q":q,"ids":ids,"size":size,"fields":fields,"sort":sort,"sort_type":sort_type,"aggs":aggs,"author":author,"subreddit":subreddit,"after":after,"before":before,"frequency":frequency,"metadata":metadata}
    
    # Get rid of unused fields
    args = {key:value for key,value in args.items() if value is not None}

    # Prep list for url reqest
    for key, value in args.items():
        # deal with search terms
        if key == "q":
            value = "\"" + value + "\""

        # make sure ints are ints
        if key in ["before","after"]:
            value = int(value)

        # Format lists as csv
        if value is list:
            temp = ""
            for el in value:
                temp = temp + el + ","
            args[key] = temp[:-1] # [:-1] to get rid of last comma
        
        # Make everything into strings
        if value is not str:
            args[key] = str(value)

    # Create url for request   
    url = "https://api.pushshift.io/reddit/search/comment/?"
    for key, value in args.items():
        # deal with spaces
        value = value.replace(" ", "%20")

        url += key + "=" + value + "&"
        
    url = url[:-1] # Get rid of last &


    # Use url to get dictionary of info
    return get_jsonparsed_data(url)

def get_sentiment_comments(term, before = None, after = None, subreddit = None):
    """
    Gets approriate comments for sentiment analysis for a specific term
    on Reddit

    input:
        - term: the string to include comments for
        - before: epoch date to include comments before
        - after: epoch date to include comments after
        - subreddit: str
    output:
        - A list of dictionaries [{'body': str, 'created_utc': int, 'score':int},...]
    """
    sort = "desc"
    sort_type = "score"
    fields = "created_utc,body,score"
    size = 500

    data = pushshift_comment(q = term, before = before, after = after,\
    subreddit = subreddit, sort = sort, sort_type = sort_type, fields = fields, size = size)

    return data["data"]

def get_binned_sentiment_comments(term, before, after, subreddit = None, numBins = 30):
    """
    gets a binned list of binned comments

    input:
        - term: the string to include comments for
        - before: epoch date to include comments before
        - after: epoch date to include comments after
        - subreddit: str
        - numBins: int number of bins
    
    output:
        - a list of lists of dictionaries
        [comment bin,...]
        comment bin = [{comment dict},...]
        comment dict = {'body': str, 'created_utc': int, 'score':int}
    """
    bins = []
    binLength = (after - before) / numBins
    for i in range(0, numBins):
        thisBin = get_sentiment_comments(term, before + binLength * i, before - 1 + binLength * (i + 1), subreddit)
        
        # add sentiment values
        make_sentiment(thisBin)
        
        bins.append(thisBin)

    return bins

def make_sentiment(comments: list):
    """
    gets the textblob generated sentiment value for each comment

    input:
        - comments: list of dictionaries, each one representing a comment
    """
    for comment in comments:
        blob = TextBlob(comment["body"])
        totalSentiment = 0
        for sentence in blob.sentences:
            totalSentiment += sentence.sentiment.polarity
        comment["sentiment"] = totalSentiment / len(blob.sentences)
    return comments

def get_simplified_sentiment_bins(term, before, after, subreddit = None, numBins = 30):
    """
    gets the final list of binned comments

    input:
        - term: the string to include comments for
        - before: epoch date to include comments before
        - after: epoch date to include comments after
        - subreddit: str
        - numBins: int number of bins
    
    output:
        - a touple of lists ([epochdate,...],[sentiment,...])
        - formated for easy plotting
        - epochdates and sentiments are the average value from their bin
    """
    sentiBins = get_binned_sentiment_comments(term, before, after,\
    subreddit = subreddit, numBins = numBins)

    simplifiedSentiments = ([],[])

    # Get the average values for every bin
    for sentiBin in sentiBins:
        totalEpoch = 0
        totalSenti = 0

        for comment in sentiBin:
            totalEpoch += comment["created_utc"]
            totalSenti += comment["sentiment"]
        
        averageEpoch = int(totalEpoch / len(sentiBin))
        averageSenti = totalSenti / len(sentiBin)

        simplifiedSentiments[0].append(averageEpoch)
        simplifiedSentiments[1].append(averageSenti)

    return simplifiedSentiments

def plot_sentiments_over_time(queries, before, after, numBins = 30):
    """
    Displays a histogram of queries' sentiment over time

    Input:
        - queries: [(term, subreddit),...]
        - before: int epoch value
        - after: int epoch value
    """
    fig, ax = plt.subplots()

    artists = []

    for query in queries:

        # Get histogram data for query
        sentiBins = get_simplified_sentiment_bins(query[0], before, after, subreddit = query[1], numBins = numBins)

        # The beginning date of each value
        epochBinEdges = sentiBins[0]

        # The value of each bin
        binValues = sentiBins[1]

        # Format the values
        binEdges = []
        for edge in epochBinEdges:
            binEdges.append(mdate.epoch2num(edge)) # Change to num format for hist

        # Plot the date using plot_date rather than plot
        line = ax.plot_date(binEdges, binValues,ls='-',marker="None")

        artists.append(line)

    # Choose your xtick format string
    date_fmt = '%m-%d-%y'

    # Use a DateFormatter to set the data to the correct format.
    date_formatter = mdate.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)

    # Sets the tick labels diagonal so they fit easier.
    fig.autofmt_xdate()

    # Label the graph
    plt.ylabel('Sentiment')
    plt.xlabel('Date')
    plt.title('Sentiment over time')

    # Legend
    labels = [str(query[0]) + ", " + str(query[1]) for query in queries]
    plt.legend(labels,loc='upper left')

    plt.savefig("result.svg")
    plt.show()