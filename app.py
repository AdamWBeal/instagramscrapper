import time
import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import requests, re, json ,pprint
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask,render_template,request,make_response
from .InstaForm import InstaForm
import re
import timeit
import pickle

start = timeit.default_timer()

app = Flask(__name__)

posts = {}

def lord_giveth_formatting(text):
    if text.find("k")<0:
        return int((text.replace(',', '')))
    else:
        return int(float((text.replace(',', '').replace('k','')))*1000)


@app.route('/', methods=['GET', 'POST'])
def login():
    form = InstaForm()
    return render_template('funk.html',
                           title='Sign In',
                           form=form)

@app.route('/results',methods=['GET', 'POST'])
def hello_buck():
    print(request.form)
    form = InstaForm(request.form)
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')
    driver.implicitly_wait(10)
    booga = []
    tags = (form.name.data).split(",")
    posts_to_dig = form.depth.data
    thresh_hold = form.min_likes.data


    for hashtag in tags:
        media = []

        driver.get("https://www.instagram.com/explore/tags/"+hashtag)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        while len(media)<=posts_to_dig:
            print(len(media))
            posty = driver.find_elements_by_xpath("//*[@id='react-root']/section/main/article/div/div/div/div/a")

            for p in posty:
                try:
                    media.append(p.get_attribute('href'))
                except:
                    media.append(None)
            # media = driver.find_element_by_xpath("//*[@id='react-root']/section/main/article/div/div/div/div/a").get_attribute('href')


            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(0,5))
            try:
                driver.find_element_by_xpath("//a[text()='Load more']").click()
            except NoSuchElementException:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        count = 0
        with open('adopt_love_1.pkl', 'wb') as f:
                pickle.dump(media, f)

#         for post in media:
#             driver.get(post)
#             try:
#                 likes_count = lord_giveth_formatting(driver.find_element_by_xpath("//div/section/div/span/span").get_attribute('innerHTML'))
#                 vid_or_pic = driver.find_element_by_xpath("//div/section/div/span").get_attribute('innerHTML')
#                 print(type(vid_or_pic))
#             except:
#                 likes_count = 0  #May not be actually zero. Less than ~ 4, fix exception rule later
#
#
#             post_time = driver.find_element_by_xpath('//div/div/a/time').get_attribute('datetime')
#
#             if likes_count<thresh_hold:  #get
#                 media.pop(media.index(post))
#                 break
#             else:
#                 while True:
#                     try:
#                         load_more_comments = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div/article/div/div/ul/li/a[text()[contains(.,' comments')]]")
#                         driver.execute_script("document.querySelector('react-root section main div div article div div ul li a[role=button]').scrollIntoView(true);")
#                         # react-root section main div div article div div ul li a
#                         load_more_comments.click()
#                         time.sleep(random.randint(1,5))
#                     except:
#                         break
#
#                     # For videos, this grabs VIEWS.  For photos, this grabs LIKES.
#                     # views = driver.find_element_by_xpath("//div/section/div/span/span").get_attribute("innerHTML")
#
#                 comments = []
#                 for comment in driver.find_elements_by_xpath("//div/div/ul/li/span"):
#                     # print(comment.get_attribute('text'))
#                     comments.append(comment.text)
#
#                 commenters = []
#                 for commenter in driver.find_elements_by_xpath('//div/div/ul/li/a'):
#                     commenters.append(commenter.text)
#
#                 # comments = [comments]
#                 # commenters = [commenters]
#                 num_likes_vid = 'pic'
#                 if 'likes' not in vid_or_pic:
#                     view_likes = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div/section/div/span')
#                     view_likes.click()
#                     num_likes_vid = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div/section/div/div/div/span')
#                     num_likes_vid = num_likes_vid.text
#                 # posts['vid_or_pic'] = vid_or_pic
                posts['url'] = post
                posts['comments'] = comments
                posts['post_time'] = post_time
                posts['access_time'] = datetime.datetime.now()
                posts['num_likes'] = likes_count
                posts['commenter'] = commenters
                posts['vid_likes'] = num_likes_vid

                temp = pd.DataFrame.from_dict(posts)
                temp.to_csv('{}.csv'.format(count))
#
                # name = driver.find_element_by_xpath("//header/div/div/div/a")
                # profiles.append(name.get_attribute("href"))
            # except NoSuchElementException:
            #     continue
            # finally:
                driver.back()
                count += 1
            # booga.extend(get_profile_data(list(set(profiles)),hashtag))

    driver.close()
    csv = pd.DataFrame(posts).to_csv(encoding="utf-8")
    response = make_response(csv)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
#
#     # return response
#
# stop = timeit.default_timer()
#
# print(stop - start)
