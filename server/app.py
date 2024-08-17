# app.py
from flask import Flask, jsonify, request

app = Flask(__name__)

# SETUP THE MONGO_CONNECTION
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Access the MongoDB URI
mongo_uri = os.getenv('MONGO_URI')

uri = mongo_uri if mongo_uri else "mongodb://localhost:27017"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["linkedin-scrap"]
posts_collection = db["posts"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def serialize(posts) :
    for post in posts:
        post["_id"] = str(post["_id"]);
        print(post["createdAt"])
    return posts
# Route to get all posts
@app.route('/posts', methods=['POST'])
def get_posts():
    filter = request.get_json()
    status = filter.get("status", "qualified") if filter  else "qualified";
    if filter and filter.get("date") :
        date_str = filter["date"]
        start_date = datetime.strptime(date_str, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
    else :
        start_date = date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=-2);
        end_date = start_date + timedelta(days=3)

    # Create the start and end datetime range for the day
    
    posts = serialize(list(posts_collection.find(
        {"status": status,
        "createdAt": {
            "$gte": start_date,
            "$lt": end_date
        }
        })));
    return jsonify(posts)

# Route to create a new post
@app.route('/update', methods=['POST'])
def create_post():
    new_post = request.get_json()
    if not (new_post and new_post.get("_id")):
        new_post["updatedAt"] = datetime.today();
    post = posts_collection.update(new_post)
    return jsonify(new_post), 201

if __name__ == '__main__':
    app.run(debug=False)
