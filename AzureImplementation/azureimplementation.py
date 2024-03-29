import pandas as pd
import IPython
import nltk
import matplotlib.pyplot as plt
import math
import http.client, urllib.request, urllib.parse, urllib.error, base64, json, urllib
import speech_recognition as sr
import numpy as np

from io import BytesIO
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from string import punctuation
from textblob import TextBlob as tb
from string import punctuation

# Create holding variables
speechKey = '35da50b01bfb4066a6347288b05bb324'
soundFile = 'bush-clinton_debate_waffle.wav'
textAnalyticsURI = 'australiaeast.api.cognitive.microsoft.com'
textKey = '82f1c2b1358c48c28b599afd04866914'
text_file = "Output.txt"
normalized_file = "NormalizedText.txt"
phrases_file = "Phrases.txt"
transcriptTxt = ""

# Transcribe the audio
def transcribe_audio(soundFile):
    r = sr.Recognizer()
    with sr.AudioFile(soundFile) as source:
        audio = r.record(source)

    try:
        transcription = r.recognize_bing(audio, key=speechKey)
        with open("Output.txt", "w") as text_file:
            text_file.write(transcription)
        print(transcription)
        return text_file
    except sr.UnknownValueError:
        print("The audio was unclear")
    except sr.RequestError as e:
        print("Something went wrong; {0}".format(e))

# Normalize the text file
def normalize_text(text_file):
    transcript = open(text_file, "r")
    transcriptTxt = transcript.read()

    # remove numeric digits
    transcriptTxt = ''.join(c for c in transcriptTxt if not c.isdigit())

    # remove punctuation and make lower case
    transcriptTxt = ''.join(c for c in transcriptTxt if not c in punctuation).lower()

    # print normalized text
    print('NORMALIZED TEXT:') 
    with open("NormalizedText.txt","w") as normalize_text:
        normalize_text.write(transcriptTxt)
    print(transcriptTxt)
    return normalize_text

# Get Frequency Distribution of words
def get_frequency_distribution(normalize_text):
    # Open and read the file
    freqWords = open(normalize_text, "r")
    freqWordstTxt = freqWords.read()
    freqWords_file = open("FreqWords.txt", "w")

    # Removes stop words
    freqWordstTxt = ' '.join([word for word in freqWordstTxt.split() if word not in (stopwords.words('english'))])

    words = nltk.tokenize.word_tokenize(freqWordstTxt)
    fdist = FreqDist(words)
    count_frame = pd.DataFrame(fdist, index=[0]).T
    count_frame.columns = ['Count']
    # TODO: Fix, only prints the count of words
    count_frame.to_csv(freqWords_file, header=None, index=['Count'], sep=' ', mode='a')
    
    
# Extract key phrases from the document
def key_phrases(normalize_text):

    phrases = open(normalize_text, "r")
    phrasesTxt = phrases.read()

    headers = {
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Key': textKey,
        'Accept': 'application/json'
    }

    params = urllib.parse.urlencode({})

    body = {
        "documents": [
            {
                "language": "en",
                "id": "1",
                "text": phrasesTxt
            }  
        ]
    }

    try:
        conn = http.client.HTTPSConnection(textAnalyticsURI)
        conn.request("POST", '/text/analytics/v2.0/keyPhrases?%s' % params, str(body), headers)
        response = conn.getresponse()
        data = response.read()
        phrases_file = open("Phrases.txt","w")

        parsed = json.loads(data.decode('utf-8'))
        for document in parsed['documents']:
            print("Document " + document["id"] + " key phrases: ")
            for phrase in document['keyPhrases']:
                phrases_file.write("%s\n" % phrase)
                print(" " + phrase)                
            print("-----------------------")
        conn.close()
    except Exception as e:
        print('Error:')
        print(e)

def get_sentiment(normalize_text):
    # Read the file
    sentiment = open(normalize_text, 'r')
    sentimentTxt = sentiment.read()
    # Analyse the text
    headers = {
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Key': textKey,
        'Accept': 'application/json'
    }

    params = urllib.parse.urlencode({})

    body = {
        "documents": [
            {
                "language": "en",
                "id": "1",
                "text": sentimentTxt
            }  
        ]
    }

    try:
        conn = http.client.HTTPSConnection(textAnalyticsURI)
        conn.request("POST", "/text/analytics/v2.0/sentiment?%s" % params, str(body), headers)
        response = conn.getresponse()
        data = response.read()
        parsed = json.loads(data.decode('utf-8'))
        for document in parsed['documents']:
            sentiment = ""
            if document["score"] >= 0.5:
                sentiment = "positive"
            else:
                sentiment = "negative"
            print("Conversation " + document["id"] + ": = " + sentiment)
            print("Score: " + str(document["score"]))
            with open("SentimentScore.txt", "w") as sentiment_file:
                sentiment_file.write(document["id"] + ": = " + sentiment + "\n")
                sentiment_file.write("Score: " + str(document["score"]))
        conn.close()
    except Exception as e:
        print(e)

def main():
    transcribe_audio(soundFile)
    normalize_text(text_file)
    get_frequency_distribution(normalized_file)
    key_phrases(normalized_file)
    get_sentiment(normalized_file)

if __name__ == "__main__":
    main()


