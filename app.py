import time
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
app = Flask(__name__)

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
            username = data["entry_data"]["ProfilePage"][0]["user"]["username"]
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
        media = []
        # profiles = []
        posts = {}

        driver.get("https://www.instagram.com/explore/tags/"+hashtag)
        # elem = driver.find_element_by_xpath("//*[@id='react-root']/section/main/article/div/div/div/div/a")
        # elem.click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        while len(media)<=posts_to_dig:
            print(len(media))
            media = driver.find_elements_by_xpath("//*[@id='react-root']/section/main/article/div/div/div/div")

            try:
                driver.find_element_by_xpath("//a[text()='Load more']").click()
            except NoSuchElementException:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        for dish in media:
            # ActionChains(driver).move_to_element(dish).perform()
            link_to_post = dish.find_element_by_xpath("//a").get_attribute("href")
            dish.click()
            popup = driver.find_element_by_xpath("//body/div/div/div/div/article")
            #WebDriverWait(driver, 10).until(EC.presence_of_element_located(hashtag.find_element_by_xpath("//a/div/ul/li/span")))

            # IF YOU WANT TO IMPOSE A MINIMUM LIKE COUNT
            try:
                likes_count = lord_giveth_formatting(popup.find_element_by_xpath("//div/section/div/span/span").get_attribute('innerHTML'))
                if likes_count<thresh_hold:
                    media.pop(media.index(dish))
                    continue
                else:
                    while True:

                        try:
                            load_more_comments = popup.find_element_by_xpath("//div/div/ul/li/a[text()[contains(.,' comments')]]")
                            driver.execute_script("document.querySelector('body div div div div article div div ul li a[role=button]').scrollIntoView(true);")

                            load_more_comments.click()
                            time.sleep(random.randint(.5,5))
                        except:
                            break
                    post_id = link_to_post  # Todo: extract ID from link?

                    # For videos, this grabs VIEWS.  For photos, this grabs LIKES.
                    # metadata["views"] = popup.find_element_by_xpath("//div/section/div/span/span").get_attribute("innerHTML")

                    comments = []
                    for comment in popup.find_elements_by_xpath("//div/div/ul/li/span"):
                        comments.append(comment.get_attribute("text"))
                    posts[post_id] = comments
                    temp = pd.DataFrame.from_dict(posts)
                    temp.to_csv('{}.csv'.format(post_id))
                    count += 1
                # name = popup.find_element_by_xpath("//header/div/div/div/a")
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

    return response
