# PREAMBLE

import re
import time
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os.path import dirname, join, abspath, exists
import os
import itertools


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
        self.pages = json.load(open(self.pages_filepath))  if exists(self.pages_filepath) else {}
        self.posts_filepath = "seeds/instagram_post_details.json"
        self.posts = json.load(open(self.posts_filepath)) if exists(self.posts_filepath) else {}
        self.post_count = int(1)
        self.max_hours = float(0.1)


    def start_scraping(self):
        self.start_time = time.time()
        for page_reference, page_dict in self.pages.items():
            if ((time.time() - self.start_time) / 3600) < self.max_hours:
                id_ = page_dict["id"]
                page_type = page_dict["type"]
                new_posts, mentions = list(zip(
                      *[self.process_link(link,id_) 
                          for link in self.recent_post_links_from_user(id_, self.post_count)
                          if not self.posts.get(link, False)]
                )) 
        self.posts.update(new_posts)
        self.driver.quit()

    def recent_post_links_from_user(self, username, post_count):
        url = "https://www.instagram.com/" + username + "/"
        self.driver.get(url)
        post = 'https://www.instagram.com/p/'
        number_of_posts = len(self.driver.find_elements_by_class_name('u7YqG'))
        post_links = []
        if 'This Account is Private' not in self.driver.page_source and \
                "Sorry, this page isn't available." not in self.driver.page_source:
            if number_of_posts < self.post_count:
                self.post_count = number_of_posts
            while len(post_links) < self.post_count:
                links = [a.get_attribute('href') for a in self.driver.find_elements_by_tag_name('a')]
                for link in links:
                    if post in link and link not in post_links:
                        post_links.append(link)
                scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
                self.driver.execute_script(scroll_down)
            else:
                self.driver.stop_client()
                return post_links[:self.post_count]
        self.driver.stop_client()
        return post_links[:self.post_count]


    def insta_link_details_by_class(self, url, page_id):
        with open(self.comment_js) as collect_script:
            code = collect_script.read()
        self.driver.get(url)
        self.driver.execute_script(code)
        comments = self.driver.execute_script('return window.comments')
        description = self.driver.execute_script(f'document.querySelectorAll(\'.eo2As .gElp9.PpGvg\')')
        if description:
            description, comments = comments
        page = self.driver.page_source
        post_details = dict(page_id=page_id, post_link=url, comments=comments, description=description,
                            hashtags='', mentions='', scrape_timestamp=str(datetime.now()),post_timestamp='')
        return post_details


    def process_link(self, post_link, page_id):
        new_post_details = self.insta_link_details_by_class(post_link, page_id)
        exit()
        flattened_mentions = [] 
        for mention in new_post_details['mentions'] + new_post_details['hashtags']:
            if isinstance(mention,list):
                for mention_ in mention:
                    flattened_mentions.append(mention_)
            else: 
                flattened_mentions.append(mention)
        pages = create_pages_dict(flattened_mentions, new_post_details)
        return new_post_details, pages

    def find_hashtags(comment):
        hashtags = re.findall(r'#\w+', comment, re.UNICODE)
        if (len(hashtags) > 1) & (len(hashtags) != 1):
            return hashtags
        elif len(hashtags) == 1:
            make_hashtag_list = [hashtags[0]]
            return make_hashtag_list
        else:
            return []


    def find_mentions(comment):
        mentions = re.findall(r'@\w+', comment, re.UNICODE)
        if (len(mentions) > 1) & (len(mentions) != 1):
            return mentions
        elif len(mentions) == 1:
            make_mention_list = [mentions[0]]
            return make_mention_list
        else:
            return []


    def create_pages_dict(pages_list, post_info):
        pages_info = {} 
        for page_reference in pages_list:
            page_dict = {
                    "id":page_reference[1:],
                    "last_collected_timestamp": None
                    }
            pages_info[page_reference] = page_dict
        return pages_info

