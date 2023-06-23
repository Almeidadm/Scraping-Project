from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from scrapers.scrapers_factory import ScraperFactory
import yaml
import logging


app = Flask(__name__)


@app.route('/loading')
def scrape(query, method):

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    df = pd.DataFrame({"title": [], "price": [], "url": [], "website": []})
    for website in config:
        logging.info(f"Collecting website {website} with method {method}")
        print("Scraping ", website)
        scraper = ScraperFactory.create_scraper(method, **config[website])
        aux = scraper.scrape(query)
        aux['website'] = website
        df = pd.concat([df, aux], ignore_index=True)

    print("collected:")
    print(df.groupby("website").count())
    df.to_csv("collected.csv")

    return redirect(url_for('result.html', df=df, df_result=df.to_html(index=False)))


@app.route('/result', methods=['GET', 'POST'])
def display_dataframe(df, df_result):
    # Render the DataFrame using a template

    if request.method == 'POST':
        # Filter the DataFrame based on user input
        filter_name = request.form.get('title')
        filtered_df = df[df['title'].str.contains(str(filter_name))]
        return render_template('result.html', df=df, df_result=filtered_df.to_html(index=False))

    return render_template('result.html', df=df, df_result=df_result)


@app.route('/', methods=['GET', 'POST'])
def process_query():
    if request.method == 'POST':
        query = request.form.get('query')
        method = request.form.get('method')

        return render_template("loading.html", query=query, method=method)

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
