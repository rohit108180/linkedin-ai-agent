#!/usr/bin/env python
# coding: utf-8

# In[10]:


# !pip install selenium 
# !pip install beautifulsoup4
# !pip install python-docker
# !pip install gorq
#!pip install webdriver-manager
#!pip install lxml
#!pip install spacy
#!python3 -m spacy download en_core_web_lg
#!python3 -m pip install "pymongo[srv]"


# In[13]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time
import os
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options

# Create a new instance of the ChromeOptions class
chrome_options = Options()

# Add the headless argument to the options
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
print("Imported all libraries")
# Load environment variables from .env file
load_dotenv()

# Access the MongoDB URI
passwordL = os.getenv('LINKEDIN_PASSWORD')
usernameL = os.getenv('LINKEDIN_USERNAME')

if not passwordL or not usernameL:
    raise Exception("Password or Username not set in env")
    
# Creating a webdriver instance
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options =chrome_options)

print("driver imported")
# This instance will be used to log into LinkedIn

# Opening linkedIn's login page
driver.get("https://linkedin.com/uas/login")

# waiting for the page to load
time.sleep(5)

print("login page loaded")
# entering username
username = driver.find_element(By.ID, "username")

# In case of an error, try changing the element
# tag used here.

# Enter Your Email Address
username.send_keys(usernameL) 


# entering password
pword = driver.find_element(By.ID, "password")
# In case of an error, try changing the element 
# tag used here.

# Enter Your Password
pword.send_keys(passwordL)	 
# Clicking on the log in button
# Format (syntax) of writing XPath --> 
# //tagname[@attribute='value']
driver.find_element(By.XPATH, "//button[@type='submit']").click()
# In case of an error, try changing the
# XPath used here.

# profile_url = "https://www.linkedin.com/feed"
 
# driver.get(profile_url)  






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


# In[15]:


start = time.time()

# will be used in the while loop
initialScroll = 0
finalScroll = 1000
Scrape_time = int(os.getenv("SCRAPE_TIME")) or 60
print("initiated scraping for", Scrape_time, " secs")
while True:
	driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
	# this command scrolls the window starting from
	# the pixel value stored in the initialScroll 
	# variable to the pixel value stored at the
	# finalScroll variable
	initialScroll = finalScroll
	finalScroll += 1000

	# we will stop the script for 3 seconds so that 
	# the data can load
	time.sleep(3)
	# You can change it as per your needs and internet speed

	end = time.time()

	# We will scroll for 20 seconds.
	# You can change it as per your needs and internet speed

	if round(end - start) > Scrape_time:
		break


# In[18]:

print("scrolling complete")
src = driver.page_source
 
# Now using beautiful soup
soup = BeautifulSoup(src, 'lxml')
# f = open("feed.txt", "w")
# f.write(src)
# f.close()


# In[ ]:





# In[19]:


# fie-impression-container
feeds = soup.find_all('div', {'id': 'fie-impression-container'})


# In[20]:


print('successfully fetched the feeds from the htmml page. No of scraped feeds : ' ,len(feeds))


# In[21]:


posts = []
# getting the names and info about of POSTER
for feed in feeds:
    poster = feed.find('span', {'class': 'update-components-actor__name'})
    if poster :
        poster = poster.find('span', {'class': 'visually-hidden'}).get_text()
        
    
    poster_bio = feed.find('span', {'class': 'update-components-actor__description'})
    if poster_bio :
        poster_bio = poster_bio.find('span', {'class': 'visually-hidden'}).get_text()
    if poster == "LinkedIn for Marketing" or poster == "poster Indian Startup News" or poster_bio == "Promoted" or not poster or not poster_bio:
        continue
    profile = feed.find('a', {'class': 'update-components-actor__sub-description-link'})
    profile = profile["href"] if profile else profile;
    feed_text = feed.find('span', {'class': 'break-words tvm-parent-container'});

    hrefs = feed_text.find_all("a") if feed_text else []
    href_map = {}
    for href in hrefs:
        link_text = href.get_text() if href else ""
        if link_text.find("hashtag#") != -1 or link_text == "" :
            continue;
        href_map[href.get_text()] = href["href"] if href else href;
    post = {}
    post["poster"] = poster;
    post["poster_bio"] =  poster_bio;
    post["profile"] =  profile;
    post["feed_text"] =  feed_text.get_text() if feed_text else feed_text
    post["href_map"] = href_map;
    post["createdAt"] = datetime.utcnow()
    post["status"] = "pending"
    posts.append(post)
    print("\n")
    
    
    
print("after filtering unwanted posts and converting into req objects : ", len(posts))

# SAVE THE DATA TO THE MONGO DB

db = client["posts"]
posts_collection = db["posts"]

if len(posts):
    posts_collection.insert_many(posts)
    print("saved pending posts to mongodb : " ,len(posts))
else :
    raise Exception("no posts were filtered")
    

from groq import Groq
groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    raise Exception("groq key not found")
client = Groq(
    # This is the default and can be omitted
    api_key=groq_api_key,
)

print("initiated groq")

# In[26]:


PROMT1 = "You are my social media manager. I will provide you with a post, and you must tell me if it aligns with my interests. Response: You can only reply with either 'yes' or 'no'. Do not include any additional words or sentences. My Interest: I am seeking new opportunities in software development roles, having graduated in 2024 with around 1 year of experience as a full-stack developer (front-end and back-end). I am also interested in roles such as software engineer, web developer, backend engineer, frontend developer, and full-stack engineer. Posts mentioning hiring opportunities, offering referrals, or related to these roles are of the highest interest to me."
PROMT2 = "You are my social media manager , i will give you a post and you have to tell me if that post is good for my interest or not. RESPONSE: you can only respond in one word with either 'yes' or 'no',  MY INTEREST : I am looking for new opportunites in the software engineer, backend engineer, frontend developer,full-stack engineer and related roles,  i passed out in 2024 from a Tier 1 college and i have around 1 year of experience but i can take an opportunity if it is for freshers, I am working as a softwa developer and can work on both frontends and back ends, any post which mentions an hiring opportunity or providing reffral are my of AT MOST INTEREST, Also provide the reason if you are answering with no and think this post is not relevant to me."


# In[27]:


# !pip install groq

def isRelevant( query, prompt = PROMT2, temp = 1):
    if not query :
        return False
    try : 
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
        return isQualified
    except Exception as e:
        # Catches any exception not caught by previous except blocks
        print(f"An unexpected error occurred: {e}")


# In[28]:


fetchStatus= "pending"
pending_posts = list(posts_collection.find({"status": fetchStatus}))
print("fetched pending posts for groq to complete: ",len(pending_posts))


# In[36]:


shouldSave = os.getenv("SAVE_PENDING") == "true"
if shouldSave  :
    print("saving the posts")
else :
    print("not saving the scraped posts")
for post in posts:
    isQualified = isRelevant(post["feed_text"], None )
    # isQualified = isRelevant(post["feed_text"]) if not isQualified else None
    if isQualified :
        post["status"] = "qualified"
        print("Qualified post")
    else :
        post["status"] = "unqualified"
        print("Non qualified post")
    if shouldSave :
        posts_collection.replace_one({"_id": post["_id"]}, post)


# In[30]:


qualified_posts = list(filter(lambda post: post["status"] == "qualified", posts))


# In[31]:


print("Qualified posts : ",len(qualified_posts))


# In[ ]:




