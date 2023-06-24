from flask import Flask, render_template, request, jsonify
from main import scrape
from utils.database import DataFrameDB


app = Flask(__name__)

db = DataFrameDB("data.db")
db.connect()

event_dict = {}


@app.route('/loading/', methods=['GET','POST'])
def loading():
    method = request.form['method']
    query = request.form['query']

    df = scrape(query, method)
    db.save_dataframe(df)

    return render_template('loading.html', method=method, query=query)


@app.route('/results', methods=['GET','POST'])
def results():
    data = db.fetch_data("SELECT * FROM data")

    return jsonify(data)


@app.route('/')
def process_query():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
