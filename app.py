from flask import Flask
import time
import threading
import requests
from datetime import datetime
import datetime as dt
from pymongo import MongoClient
import pymongo
import json
import os
from dotenv import load_dotenv


app = Flask(__name__)
app.config['DEBUG'] = True
load_dotenv()


# YOUTUBE API CONFIG
YOUTUBE_API_KEY1 = os.getenv('YOUTUBE_API_KEY1')
YOUTUBE_API_KEY2 = os.getenv('YOUTUBE_API_KEY2')
current_youtube_api_key = YOUTUBE_API_KEY1
SEARCH_QUERY = 'Elon Musk'
last_fetched_timestamp = '2023-08-17T08:28:00Z'
YOUTUBE_API_URL = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&order=date&maxResults=10&q={SEARCH_QUERY}&publishedAfter={last_fetched_timestamp}'

# MONGODB CONFIG
mongo_cluster_url = os.getenv('MONGO_DB_URI')
mongo_db_name = os.getenv('DB_NAME')
mongo_collection_name = os.getenv('COLLECTION_NAME')

cluster = MongoClient(mongo_cluster_url)
db = cluster[mongo_db_name]
collection = db[mongo_collection_name]

collection.create_index([('publish_datetime', pymongo.DESCENDING)], name='publishTimeIndex', default_language='english')

nextPageToken = None

def fetch_and_store_videos():
    global last_fetched_timestamp
    global nextPageToken
    global current_youtube_api_key

    current_utc_datetime = dt.datetime.utcnow()
    last_fetched_timestamp = current_utc_datetime.isoformat("T") + "Z"

    next_page_token_param = f'&pageToken={nextPageToken}' if nextPageToken else ''
    api_key_param = f'&key={current_youtube_api_key}'
    api_url_with_next_page = f'{YOUTUBE_API_URL}{api_key_param}{next_page_token_param}'

    response = requests.get(api_url_with_next_page)
    data = response.json()

    if data.get("error"):
        error_code = data.get("error").get("code")
        if error_code == 403:
            print("Key Changed")
            current_youtube_api_key = YOUTUBE_API_KEY2

    else:
        items = data.get("items", [])
        for item in items:
            video = {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'publish_datetime': datetime.strptime(item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                'thumbnails': item['snippet']['thumbnails'],
                # Add more fields as needed
            }
            collection.insert_one(video)

        if data.get("nextPageToken"):
            nextPageToken = data.get("nextPageToken")
            fetch_and_store_videos()
        else:
            print("Breaking process")

def background_task(interval):
    while True:
        print("Background task attempt")
        fetch_and_store_videos()
        time.sleep(interval)

@app.route('/')
def index():
    return "Background task is running!"

@app.route('/v1/response')
@app.route('/v1/response/<int:page_num>')
def response(page_num=None):
    limit = 10
    if page_num is None or page_num == 0:
        page_num_val = 1
        first_item_num = 1
        last_item_num = page_num_val * limit
    else:
        page_num_val = page_num
        first_item_num = (page_num_val * limit) - ((page_num_val - 1) * limit) + 1
        last_item_num = page_num_val * limit

    initial_sort = collection.find().sort("publish_datetime", pymongo.DESCENDING)
    last_id = initial_sort[first_item_num]['_id']

    output_videos = collection.find({'_id': {'$gte': last_id}}).sort("publish_datetime", pymongo.DESCENDING).limit(limit)

    next_url = f'/v2/response/{page_num_val + 1}'
    prev_url = f'/v2/response/{page_num_val - 1}'

    output = {
        'Response': 'Success',
        'Next Url': next_url,
        'Prev Url': prev_url,
    }

    output_index = 0
    for video in output_videos:
        output_index = output_index + 1
        output[output_index] = {
            'Title': video['title'],
            'Description': video['description']
        }

    json_object = json.dumps(output, indent=8)

    return json_object

if __name__ == '__main__':
    interval_seconds = 20
    task_thread = threading.Thread(target=background_task, args=(interval_seconds,))
    task_thread.start()

    app.run(debug=True)
