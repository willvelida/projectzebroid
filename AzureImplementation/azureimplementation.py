import pandas as pd
import IPython
import nltk
import matplotlib.pyplot as plt
import math
import http.client, urllib.request, urllib.parse, urllib.error, base64, json, urllib
import speech_recognition as sr

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
    print('NORMALIZED TEXT:' + transcriptTxt)
    return transcriptTxt

def key_phrases(transcriptTxt):
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
                "text": transcriptTxt
            }  
        ]
    }

    try:
        conn = http.client.HTTPSConnection(textAnalyticsURI)
        conn.request("POST", '/text/analytics/v2.0/keyPhrases?%s' % params, str(body), headers)
        response = conn.getresponse()
        data = response.read()

        parsed = json.loads(data.decode('utf-8'))
        # TODO: Document not getting read
        print(parsed)
        for document in parsed['documents']:
            print("Document " + document["id"] + " key phrases: ")
            for phrase in document['keyPhrases']:
                print(" " + phrase)
            print("-----------------------")
        conn.close()
    except Exception as e:
        print('Error:')
        print(e)

def main():
    transcribe_audio(soundFile)
    normalize_text(text_file)
    key_phrases(transcriptTxt)

if __name__ == "__main__":
    main()


