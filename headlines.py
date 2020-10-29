import os
import feedparser
from dotenv import load_dotenv
from flask import Flask
from flask import render_template, request
import requests

load_dotenv()
app = Flask(__name__)

RSS_FEED = {
    "bbc":"http://feeds.bbci.co.uk/news/rss.xml",
    "cnn":"http://rss.cnn.com/rss/edition.rss",
    "fox":"http://feeds.foxnews.com/foxnews/latest",
    "iol":"http://www.iol.co.za/cmlink/1.640"
}

DEFAULTS = {
    "publication":"bbc",
    "city":"Lagos,Nigeria"
}

@app.route("/")
def home():
    # Get headlines, based on user input
    publication = request.args.get("publication")
    if not publication:
        publication = DEFAULTS["publication"]
    articles = get_news(publication)
    # Get weather from location based on user input
    city = request.args.get("city")
    if not city:
        city = DEFAULTS["city"]
    weather = get_weather(city)
    return render_template("home.html", articles=articles, weather=weather)


def get_news(query):
    if not query or query.lower() not in RSS_FEED:
        publication = "bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEED[publication])
    return feed["entries"]

def get_weather(query):
    api_url = "http://api.openweathermap.org/data/2.5/weather"
    r = requests.get(api_url, params={
        "appid":os.getenv("WEATHER_API_KEY"),
        "units":"metric",
        "q":query
    }).json()
    weather = None
    if r.get("weather"):
        weather = {
            "description": r["weather"][0]["description"],
            "temperature": r["main"]["temp"],
            "city":r["name"], "country":r["sys"]["country"]
        }
    return weather


if __name__ == '__main__':
    app.run(port=5000, debug=True)