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
    "city":"Lagos,Nigeria",
    "currency_from":"GBP",
    "currency_to":"USD"
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
    # Get currencies to be converted from user
    currency_from = request.args.get("currency_from")
    currency_to = request.args.get("currency_to")
    if not currency_from:
        currency_from = DEFAULTS["currency_from"]
    if not currency_to:
        currency_to = DEFAULTS["currency_to"]
    rate, currencies = get_rate(currency_from, currency_to)

    return render_template(
        "home.html", articles=articles,
        weather=weather, currency_from=currency_from,
        currency_to=currency_to, rate=rate,
        currencies=sorted(currencies)
    )


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

def get_rate(frm, to):
    currency_url = "https://openexchangerates.org//api/latest.json"
    r = requests.get(currency_url, params={
        "app_id":os.getenv("EXCHANGE_API_KEY")
    }).json().get("rates")
    frm_rate = r.get(frm.upper())
    to_rate = r.get(to.upper())
    return (round(to_rate/frm_rate, 3), r.keys())

if __name__ == '__main__':
    app.run(port=5000, debug=True)