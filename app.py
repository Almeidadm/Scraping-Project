from flask import Flask, render_template, request
import pandas as pd
from scraper.src.scrapers_factory import ScraperFactory
from scraper.main import scrape, db
import asyncio


app = Flask(__name__)


@app.route('/loading')
def loading():
    return render_template('loading.html')


@app.route('/results')
def results():
    data = db.fetch_data("SELECT * FROM data")

    return render_template('results.html', data=data)


async def perform_web_scraping(query, method):
    df = scrape(query, method)
    db.save_dataframe(df)


@app.route('/', methods=['GET', 'POST'])
def process_query():
    if request.method == 'POST':
        query = request.form.get('query')
        method = request.form.get('method')

        asyncio.create_task(perform_web_scraping(query, method))

        return render_template("loading.html", query=query, method=method)

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
