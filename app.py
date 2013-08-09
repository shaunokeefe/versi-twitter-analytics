from flask import Flask
from flask import render_template
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def hello_world():
        return 'Hello World!'

@app.route('/map/')
def map(name=None):

    db_name = 'tweet_db'
    collection_name = 'user_collection'
    db_client = MongoClient()
    db = db_client[db_name]
    collection = db[collection_name]

    users = collection.find()
    return render_template('map.html', users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
#shauns comment


