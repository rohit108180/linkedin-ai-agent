#!/usr/bin/env python
# coding: utf-8

# In[3]:


# SETUP THE MONGO_CONNECTION
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
from groq import Groq
client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)

mongo_uri = os.getenv('MONGO_URI')
# SETUP THE MONGO_CONNECTION
uri = mongo_uri if mongo_uri else "mongodb://localhost:27017"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# In[4]:


db = client["posts"]
posts_collection = db["posts"]


# In[77]:


PROMT1 = "You are my social media manager. I will provide you with a post, and you must tell me if it aligns with my interests. Response: You can only reply with either 'yes' or 'no'. Do not include any additional words or sentences. My Interest: I am seeking new opportunities in software development roles, having graduated in 2024 with around 1 year of experience as a full-stack developer (front-end and back-end). I am also interested in roles such as software engineer, web developer, backend engineer, frontend developer, and full-stack engineer. Posts mentioning hiring opportunities, offering referrals, or related to these roles are of the highest interest to me."
PROMT2 = "You are my social media manager , i will give you a post and you have to tell me if that post is good for my interest or not. RESPONSE: you can only respond in one word with either 'yes' or 'no',  MY INTEREST : I am looking for new opportunites in the software engineer, backend engineer, frontend developer,full-stack engineer and related roles,  i passed out in 2024 from a Tier 1 college and i have around 1 year of experience but i can take an opportunity if it is for freshers, I am working as a softwa developer and can work on both frontends and back ends, any post which mentions an hiring opportunity or providing reffral are my of AT MOST INTEREST, Also provide the reason if you are answering with no and think this post is not relevant to me."


# In[78]:


# !pip install groq

def isRelevant( query, prompt = PROMT2, temp = 1):
    if not query :
        return False;
    chat_completion = client.chat.completions.create(messages=[
        {
            'role': 'system',
            'content': prompt if prompt else PROMT2
        },
        {
            'role': 'user',
            'content': "This is this post" + query,
        }],
        model="llama-3.1-70b-versatile",
        temperature=temp,
        top_p=1,
        stream=False,
        stop=None,
    )
    stream  = chat_completion.choices[0].message.content
    response =""
    isQualified = stream.lower().find("yes") != -1
    print("BOT: ", stream)
    return isQualified;


# In[79]:


# #!pip install ollama
# import ollama
# # ollama.pull('llama3.1')

# def isRelevant( query):
#     if not query :
#         return False;
#     stream = ollama.chat(model='llama3.1', messages=[
#         {
#             'role': 'system',
#             'content': PROMT2
#         },
#         {
#             'role': 'user',
#             'content': "This is this post" + query,
#         }]
#     )
#     stream  = stream['message']['content']
#     response =""
#     isQualified = stream.lower().find("yes") != -1
#     print("BOT: ", stream)
#     return isQualified;
    


#     # print( "\n Chat line ", chatLine);
#     # print( "\n Chat History", chatHistory)


# In[82]:


fetchStatus= "qualified"
pending_posts = list(posts_collection.find({"status": fetchStatus}))
print(len(pending_posts))
pending_posts = pending_posts[0:100];


# In[83]:


shouldSave = input('Do you want to save') 
if shouldSave == "yes" :
    print("saving the posts")
for post in pending_posts:
    isQualified = isRelevant(post["feed_text"], None )
    # isQualified = isRelevant(post["feed_text"]) if not isQualified else None
    if isQualified :
        post["status"] = "qualified"
        print(post["feed_text"]) if fetchStatus == "unqualified" else None;
    else :
        post["status"] = "unqualified"
        print(post["feed_text"]) if fetchStatus == "qualified" else None;
    if shouldSave == "yes" :
        posts_collection.replace_one({"_id": post["_id"]}, post)


# In[10]:


qualified_posts = list(filter(lambda post: post["status"] == "qualified", pending_posts))


# In[11]:


for post in qualified_posts:
    print(post["poster"] +  " :  "  + post["poster_bio"]) 
    print("profile" , post["profile"]);
    print("feed_text" , post["feed_text"])  if post else post
    print("href",post["href_map"])
    print("\n")


# In[12]:


len(qualified_posts)


# In[ ]:




