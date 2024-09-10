#!/usr/bin/env python
# coding: utf-8

# In[10]:


# !pip install selenium 
# !pip install beautifulsoup4
#
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
import spacy
nlp = spacy.load('en_core_web_lg')
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Access the MongoDB URI
passwordL = os.getenv('LINKEDIN_PASSWORD')


# Creating a webdriver instance
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
# This instance will be used to log into LinkedIn

# Opening linkedIn's login page
driver.get("https://linkedin.com/uas/login")

# waiting for the page to load
time.sleep(5)

# entering username
username = driver.find_element(By.ID, "username")

# In case of an error, try changing the element
# tag used here.

# Enter Your Email Address
username.send_keys("rohit108180@gmail.com") 

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






# In[14]:


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
	if round(end - start) > 600:
		break


# In[18]:


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


print(len(feeds))


# In[21]:


posts = [];
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
    print(post)
    print("\n")
    
    
    


# In[ ]:


# # Extracting the HTML of the complete introduction box
# # that contains the name, company name, and the location
# feeds = soup.find_all('div', {'class': 'feed-shared-update-v2__description-wrapper'})
 


# In[ ]:


# feed_texts = [ feed.find('span', {'class': 'break-words tvm-parent-container'}) for feed in feeds]
# for feed_text in feed_texts:
#     print(feed_text.get_text())
#     print(feed_text.get_text().find("hiring"))
#     print("\n")


# In[ ]:


# Given text
# given_text = nlp("🚀 We're Hiring! Join Our Dynamic Team! We're excited to announce that [Company Name] is expanding, and we're looking for passionate individuals to join us. If you're someone who thrives in a fast-paced environment and loves solving challenging problems, we want to hear from you! Open Positions:Software EngineerLocation: [City, Country]Apply HereData ScientistLocation: [City, Country]Apply HereProduct ManagerLocation: [City, Country]Apply HereWhy [Company Name]?Competitive salary and benefitsOpportunity to work with a talented teamFlexible working hours and remote work optionsProfessional development and growth opportunitiesInterested?Click on the links above to apply or visit our Careers Page. Share this post with anyone who might be a great fit! Let's build something amazing together.#Hiring #JobOpportunity #JoinOurTeam #TechJobs")
# given_text2=nlp("I am a passionate Computer Engineering student with a minor in Artificial Intelligence, currently seeking full-time Software Engineering roles. I have experience in developing and optimizing software solutions, with strong skills in C/C++, SQL, JavaScript, ReactJs, Node.js, and database management (SQL, NoSQL). I am particularly interested in positions that involve: Backend development using Node.js and SQL/NoSQL databases. API development and optimization for scalable applications. Collaborative projects in agile environments. Opportunities for growth in machine learning and AI integration. I have a proven track record of success, including leading teams in hackathons and internships where I contributed to significant performance improvements. I am looking for a role where I can leverage my technical skills and leadership abilities to contribute to innovative projects. If your company is hiring for roles that match these interests, I would love to connect! #SoftwareEngineering #BackendDevelopment #NodeJS #AI #APIDevelopment #TechJobs #Hiring");
# # Filter texts based on similarity
# threshold = 0.7  # Set your threshold

# filtered_texts = [post for post in posts if post["feed_text"] and given_text.similarity(nlp(post["feed_text"])) > threshold]


# for feed_text in filtered_texts:
#     print(feed_text)
#     print("\n")


# In[ ]:


# SAVE THE DATA TO THE MONGO DB



# In[22]:


db = client["posts"]
posts_collection = db["posts"]


# In[ ]:





# In[23]:


posts_collection.insert_many(posts)


# In[24]:


print(len(posts))
    


# In[25]:


from groq import Groq
client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)


# In[26]:


PROMT1 = "You are my social media manager. I will provide you with a post, and you must tell me if it aligns with my interests. Response: You can only reply with either 'yes' or 'no'. Do not include any additional words or sentences. My Interest: I am seeking new opportunities in software development roles, having graduated in 2024 with around 1 year of experience as a full-stack developer (front-end and back-end). I am also interested in roles such as software engineer, web developer, backend engineer, frontend developer, and full-stack engineer. Posts mentioning hiring opportunities, offering referrals, or related to these roles are of the highest interest to me."
PROMT2 = "You are my social media manager , i will give you a post and you have to tell me if that post is good for my interest or not. RESPONSE: you can only respond in one word with either 'yes' or 'no',  MY INTEREST : I am looking for new opportunites in the software engineer, backend engineer, frontend developer,full-stack engineer and related roles,  i passed out in 2024 from a Tier 1 college and i have around 1 year of experience but i can take an opportunity if it is for freshers, I am working as a softwa developer and can work on both frontends and back ends, any post which mentions an hiring opportunity or providing reffral are my of AT MOST INTEREST, Also provide the reason if you are answering with no and think this post is not relevant to me."


# In[27]:


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


# In[28]:


fetchStatus= "pending"
pending_posts = list(posts_collection.find({"status": fetchStatus}))
print(len(pending_posts))


# In[36]:


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


# In[30]:


qualified_posts = list(filter(lambda post: post["status"] == "qualified", pending_posts))


# In[31]:


len(qualified_posts)


# In[ ]:




