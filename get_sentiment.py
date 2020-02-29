from textblob import TextBlob

def make_sentiment(comments: list):
    for comment in comments:
        blob = TextBlob(comment["body"])
        totalSentiment = 0
        for sentence in blob.sentences:
            totalSentiment += sentence.sentiment.polarity
        comment["sentiment"] = totalSentiment / len(blob.sentences)
    return comments

