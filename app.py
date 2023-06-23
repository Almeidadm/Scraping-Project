from flask import Flask, render_template, request, redirect, url_for
import threading
from scraper.main import scrape
from scraper.src.database import DataFrameDB
import asyncio


app = Flask(__name__)

db = DataFrameDB("data.db")
db.connect()


@app.route('/loading/')
def loading(event):
    event.wait()

    return redirect(url_for('results'))


@app.route('/results')
def results():
    data = db.fetch_data("SELECT * FROM data")

    return render_template('results.html', data=data)


def perform_web_scraping(query, method):
    df = scrape(query, method)
    db.save_dataframe(df)


def perform_web_scraping_with_event(query, method, event):
    perform_web_scraping(query, method)
    event.set()


def perform_web_scraping_background(query, method):
    event = threading.Event()
    thread = threading.Thread(target=perform_web_scraping_with_event, args=(query, method, event))
    thread.start()
    return event


@app.route('/', methods=['GET', 'POST'])
def process_query():
    if request.method == 'POST':
        query = request.form.get('query')
        method = request.form.get('method')

        event = perform_web_scraping_background(query, method)

        return redirect(url_for("loading", event=event))

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
