import re
import time
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os.path import dirname, join, abspath, exists
import os
import itertools
import pprint
import ast


class IGScraper:
    pkg_path = dirname(abspath(__file__)) 
    comment_js = join(pkg_path,"collect_comments.js")
    def __init__(self):
        self.base_folder = abspath(os.getcwd())
        self.driver_filepath = join(self.base_folder, 'chromedriver')
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        #chrome_options.binary_location="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.driver = webdriver.Chrome(self.driver_filepath, options=chrome_options)
        self.driver.set_window_size(980, 573)

        self.pages_filepath = "seeds/instagram_pages.json"
        self.pages = ast.literal_eval(open(self.pages_filepath).read())  if exists(self.pages_filepath) else {}
        self.posts_filepath = "seeds/instagram_post_details.json"
        self.posts = ast.literal_eval(open(self.posts_filepath).read()) if exists(self.posts_filepath) else {}


    def start_scraping(self):
        self.start_time = time.time()
        pages_before_scraping = self.pages.copy()
        for page_reference, page_dict in pages_before_scraping.items():
            self.pages[page_reference]["last_scraped_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            id_ = page_dict["id"]
            page_type = page_dict["type"]
            try:
                new_posts, new_pages = list(zip(
                      *[self.process_link(link,id_) 
                          for link in self.get_recent_post_links(id_, page_type, n=3)
                          if not self.posts.get(link, False)]
                )) 
            except Exception as E:
                new_posts, new_pages = {}, {}
                print("!!!!"*1000)
                print(E)

            for post in new_posts:
               print(post['n_comments'])
               self.posts.update({post["post_link"]:post})
            self.write_posts()
        #self.driver.quit()

    def get_recent_post_links(self, page_id, type_, n=-1):
        url = "https://www.instagram.com/explore/tags/" + page_id + "/" \
            if type_ == "hashtag" \
            else "https://www.instagram.com/" + page_id + "/" 
        self.driver.get(url)
        post_links_to_scrape = []

        if 'This Account is Private' not in self.driver.page_source and \
                "Sorry, this page isn't available." not in self.driver.page_source:
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            self.driver.execute_script(scroll_down)
            time.sleep(5)
            self.driver.execute_script(scroll_down)
            time.sleep(5)
            self.driver.execute_script(scroll_down)
            post_links = self.driver.execute_script(f'return [...document.querySelectorAll("a[href*=\'/p/\'")].map(function (l) {{ return l.getAttribute("href")}})')
            for post_link in post_links:
                if not self.posts.get(post_link, False):
                    full_url = f'https://instagram.com{post_link}'
                    post_links_to_scrape.append(full_url)
        return post_links_to_scrape[:n]


    def insta_link_details_by_class(self, url, page_id):
        with open(self.comment_js) as collect_script:
            code = collect_script.read()
        self.driver.get(url)
        post_timestamp_str = self.driver.execute_script(f"return  document.querySelector('time._1o9PC.Nzb55')['dateTime']")
        post_timestamp =  datetime.strptime(post_timestamp_str,"%Y-%m-%dT%H:%M:%S.000Z")

        description = self.driver.execute_script(''' window.description = document.querySelector(\'.eo2As .gElp9.PpGvg\')
                if(window.description){
                    return {
                        "comment": window.description.innerText,
                        "html": window.description.innerHTML}
                }
                else {
                    return {
                    }
                }
                ''')

        self.driver.execute_script(code) # _async
        element = WebDriverWait(self.driver, 99999999).until(
                        EC.alert_is_present()
                )
        print("*"*1000)
        self.driver.switch_to_alert().accept()
        comments = self.driver.execute_script('return window.comments')
        if description:
            comments = comments[1:]
            hashtags, mentions = self.find_references(description['comment'], reference_type="hashtag"),\
                                 self.find_references(description['comment'], reference_type="user")
        else:
            hashtags, mentions =  [], []

        for comment in comments:
            hashtags += self.find_references(comment['comment'], reference_type="hashtag")
            mentions += self.find_references(comment['comment'], reference_type="user")

        page = self.driver.page_source
        post_details = dict(page_id=page_id, post_link=url, comments=comments, description=description,
                            n_comments=len(comments),
                            hashtags=hashtags, mentions=mentions,
                            scrape_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),post_timestamp=post_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        return post_details


    def process_link(self, post_link, page_id):
        new_post_details = self.insta_link_details_by_class(post_link, page_id)
        referenced_pages = {}
        referenced_pages.update(
                self.create_pages_dict(new_post_details['mentions'],
                    new_post_details, pages_type="user")
                )
        referenced_pages.update(
                self.create_pages_dict(new_post_details['hashtags'],
                    new_post_details, pages_type="hashtag")
                )
        return new_post_details, referenced_pages

    def find_references(self, comment, reference_type):
        reference_char = "@" if reference_type == "user" else "#"
        references = re.findall(f'{reference_char}\w+', comment, re.UNICODE)
        if len(references) > 1:
            return references 
        elif len(references) == 1:
            references = [references[0]]
            return references
        else:
            return []

    def create_pages_dict(self, pages_list, post_info, pages_type):
        pages_info = {} 
        for page_reference in pages_list:
            page_dict = {
                    "id":page_reference[1:],
                    "type": pages_type,
                    "post_where_referenced": post_info["post_link"],
                    "last_scraped_timestamp": ""
                    }
            pages_info[page_reference] = page_dict
        return pages_info

    def write_posts(self):
        if self.posts:
            with open(self.posts_filepath,"w") as posts_file: 
                    pprint.pprint(self.posts, stream=posts_file)
