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

def get_emails(s):
    regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))
    """Returns an iterator of matched emails found in string s."""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    return (email[0] for email in re.findall(regex, s) if not email[0].startswith('//'))

def lord_giveth_formatting(text):
    if text.find("k")<0:
        return int((text.replace(',', '')))
    else:
        return int(float((text.replace(',', '').replace('k','')))*1000)

def get_profile_data(profiles,tag):
    print(profiles)
    profile_dict = []
    for stuff in profiles:
        try:
            r = requests.get(stuff)
            soup = BeautifulSoup(r.content, "html5lib")
            script = soup.find('script', text=re.compile('window\._sharedData'))
            json_text = re.search(r'^\s*window\._sharedData\s*=\s*({.*?})\s*;\s*$',script.string, flags=re.DOTALL | re.MULTILINE).group(1)
            data = json.loads(json_text)
            #print json.dumps(data, indent=4, sort_keys=True)
            insta_id = data["entry_data"]["ProfilePage"][0]["user"]["id"]
            username = d3ata["entry_data"]["ProfilePage"][0]["user"]["username"]
            emails = get_emails(data["entry_data"]["ProfilePage"][0]["user"]["biography"])
            email=''
            usr_url = data["entry_data"]["ProfilePage"][0]["user"]["external_url"]
            bio = data["entry_data"]["ProfilePage"][0]["user"]["biography"]
            followers = data["entry_data"]["ProfilePage"][0]["user"]["followed_by"]["count"]
            following = data["entry_data"]["ProfilePage"][0]["user"]["follows"]["count"]
            full_name = data["entry_data"]["ProfilePage"][0]["user"]["full_name"]
            media_count = data["entry_data"]["ProfilePage"][0]["user"]["media"]["count"]
            profile_pic = data["entry_data"]["ProfilePage"][0]["user"]["profile_pic_url_hd"]
            for ema in emails:

                # email=ema.decode("utf-8", "strict")
                print(type(email+" "))
                print(email)
                break
            profile_dict.append({'insta_id':insta_id, 'username':username, 'profile_url': usr_url, 'full_name':full_name, 'bio':bio, 'followers':followers,'following':following, 'media_count':media_count, 'tag':tag,'email':email})
        except:
            print("Failed:" + str(data))
    #pd.DataFrame(profile_dict).to_csv(tag,encoding = "utf-8")
    return profile_dict


# index view function suppressed for brevity

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
        media = ['https://www.instagram.com/p/BevWWJyhJvi/?tagged=ilovemyrescue']
        # profiles = []


        # driver.get("https://www.instagram.com/explore/tags/"+hashtag)
        # elem = driver.find_element_by_xpath("//*[@id='react-root']/section/main/article/div/div/div/div/a")
        # elem.click()
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # while len(media)<=posts_to_dig:
        #     print(len(media))
        #     posty = driver.find_elements_by_xpath("//*[@id='react-root']/section/main/article/div/div/div/div/a")
        #
        #     for p in posty:
        #         try:
        #             media.append(p.get_attribute('href'))
        #         except:
        #             media.append("NO")
            # media = driver.find_element_by_xpath("//*[@id='react-root']/section/main/article/div/div/div/div/a").get_attribute('href')


            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(random.randint(2,5))
            # try:
            #     driver.find_element_by_xpath("//a[text()='Load more']").click()
            # except NoSuchElementException:
            #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        count = 0
        # with open('parrot.pkl', 'wb') as f:
        #         pickle.dump(media, f)
        for post in media:
            # ActionChains(driver).move_to_element(post).perform()

            # link_to_post = post.find_element_by_xpath("//a").get_attribute("href")

            # post.click()
            # driver = driver.find_element_by_xpath("//body/div/div/div/div/article")


            #WebDriverWait(driver, 10).until(EC.presence_of_element_located(hashtag.find_element_by_xpath("//a/div/ul/li/span")))

            # IF YOU WANT TO IMPOSE A MINIMUM LIKE COUNT

            try:
                driver.get(post)
                # page_url = driver.current_url
                # likes_count = lord_giveth_formatting(driver.find_element_by_xpath("//div/section/div/span/span").get_attribute('innerHTML'))
                likes_count = lord_giveth_formatting(driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div/section/div/span/span').get_attribute('innerHTML'))
                likes_count = int(likes_count)
                print(likes_count)
                vid_or_pic = driver.find_element_by_xpath("//div/section/div/span").get_attribute('innerHTML')
                post_time = driver.find_element_by_xpath('//div/div/a/time').get_attribute('datetime')
                print(post_time)
                if likes_count<thresh_hold:
                    media.pop(media.index(post))
                    continue
                else:
                    while True:

                        try:
                            load_more_comments = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div/article/div/div/ul/li/a[text()[contains(.,' comments')]]")
                            driver.execute_script("document.querySelector('section main div div article div div ul li a[role=button]').scrollIntoView(true);")
                            # react-root > section > main > div > div > article > div._ebcx9 > div._4a48i._277v9 > ul > li a
                            load_more_comments.click()
                            time.sleep(random.randint(4,5))
                        except:
                            print('broke here')
                            break

                    # For videos, this grabs VIEWS.  For photos, this grabs LIKES.
                    # views = driver.find_element_by_xpath("//div/section/div/span/span").get_attribute("innerHTML")

                    comments = []
                    for comment in driver.find_elements_by_xpath("//div/div/ul/li/span"):
                        # print(comment.get_attribute('text'))
                        comments.append(comment.text)

                    commenters = []
                    for commenter in driver.find_elements_by_xpath('//div/div/ul/li/a'):
                        commenters.append(commenter.text)

                    comments = [comments]
                    commenters = [commenters]


                    posts['vid_or_pic'] = vid_or_pic
                    posts['url'] = post
                    posts['comments'] = comments
                    posts['post_time'] = post_time
                    posts['access_time'] = datetime.datetime.now()
                    posts['num_likes'] = likes_count
                    posts['commenter'] = commenters

                    temp = pd.DataFrame.from_dict(posts)
                    temp.to_csv('{}.csv'.format(count))

                # name = driver.find_element_by_xpath("//header/div/div/div/a")
                # profiles.append(name.get_attribute("href"))
            except NoSuchElementException:
                continue
            finally:

                driver.back()
            #element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div[2]/div/div[2]/div/article/header/div/a[@href]")))
            #element.click()
            # driver.back()

            #driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div/article/header").click()
        # booga.extend(get_profile_data(list(set(profiles)),hashtag))

    driver.close()
    csv = pd.DataFrame(posts).to_csv(encoding="utf-8")
    response = make_response(csv)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'

    # return response

stop = timeit.default_timer()

print(stop - start)
