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

@app.route("/")
def get_news(publication="bbc"):
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEED:
        publication = "bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEED[publication])
    weather = get_weather("Lagos,Nigeria")
    return render_template(
        "home.html", articles=feed["entries"], weather=weather
    )

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
            "city":r["name"]
        }
    return weather


if __name__ == '__main__':
    app.run(port=5000, debug=True)