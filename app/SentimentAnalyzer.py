from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *
import sys
import Config

hodClient = HODClient(Config.ConfigVars['hpeKey'])
parser = HODResponseParser()
hodApp = HODApps.ANALYZE_SENTIMENT

context = {}
context["hodapp"] = hodApp

sentiments = ''


def requestCompleted(response, **context):
    global sentiments
    resp = ""
    payloadObj = parser.parse_payload(response)
    if payloadObj is None:
        errorObj = parser.get_last_error()
        for err in errorObj.errors:
            resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error, err.reason, err.detail)
    else:
        app = context["hodapp"]
        if app == HODApps.ANALYZE_SENTIMENT:
            positives = payloadObj["positive"]
            resp += "Positive:\n"
            for pos in positives:
                resp += "Sentiment: " + pos["sentiment"] + "\n"
                if pos.get('topic'):
                    resp += "Topic: " + pos["topic"] + "\n"
                if pos.get('original_text'):
                    resp += "Original_Text: " + pos["original_text"] + "\n"
                    sentiments += "sent_Original_Text:" + pos["original_text"]
                resp += "Score: " + "%f " % (pos["score"]) + "\n"
                sentiments += ":sent_Score:" + "%f " % (pos["score"]) + "\n"
                if 'documentIndex' in pos:
                    resp += "Doc: " + str(pos["documentIndex"]) + "\n"
            negatives = payloadObj["negative"]
            resp += "Negative:\n"
            for neg in negatives:
                resp += "Sentiment: " + neg["sentiment"] + "\n"
                if neg.get('topic'):
                    resp += "Topic: " + neg["topic"] + "\n"
                    resp += "Score: " + "%f " % (neg["score"]) + "\n"
                if neg.get('original_text'):
                    resp += "Original Text: " + neg["original_text"] + "\n"
                    sentiments += "sent_Original_Text:" + neg["original_text"]
                if 'documentIndex' in neg:
                    resp += "Doc: " + str(neg["documentIndex"]) + "\n"
                sentiments += ":sent_Score:" + "%f " % (neg["score"]) + "\n"
            aggregate = payloadObj["aggregate"]
            resp += "Aggregate:\n"
            resp += "Score: " + "%f " % (aggregate["score"]) + "\n"
            sentiments += "sent_Overall_Sentiment:" + aggregate["sentiment"]
            sentiments += ":sent_Overall_Score:" + "%f" % (aggregate["score"])

            resp += aggregate["sentiment"]
    return

def getSentiments(inText):
    paramArr = {}
    paramArr["text"] = inText
    paramArr["lang"] = "eng"
    hodClient.post_request(paramArr, hodApp, async=False, callback=requestCompleted, **context)
