#s!/usr/bin/env python3

import  os
import requests
from bs4 import BeautifulSoup
import json

from pathlib import Path
import re
from modules.sources.zillow.ad import ZillowAd

class ZillowScraper():
    current_directory = os.path.dirname(os.path.realpath(__file__))

    new_ads = []
    old_ad_ids = []
    exclude = []

    third_party_ads = []

    def __init__(self):
        self.third_party_ads = []
        self.old_ad_ids = []

    def get_properties(self):
        return ["url"]


    def validate_properties(self, **kwargs):
        pass

    # Pulls page data from a given Zillow url and finds all ads on each page
    def scrape_for_ads(self, old_ad_ids, exclude=[], **kwargs):
        self.new_ads = {}
        self.old_ad_ids = old_ad_ids
        self.exclude = []

        url = kwargs["url"]
        title = None
        while url:
            # Get the html data from the URL
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            # If the title doesnt exist pull it from the html data
            if title is None:
                title = self.get_title(soup)

            # Find ads on the page
            self.find_ads(soup)

            # Set url for next page of ads
            url = soup.find('a', {'title': 'Next'})
            if url:
                url = 'https://www.zillow.com' + url['href']

        return self.new_ads, title

    def find_ads(self, soup):
        # Finds all ad trees in page html.
        zillow_ads = soup.find_all("div", {"class": "result-list-container"})

        # Find all third-party ads to skip them
        # third_party_ads = soup.find_all("div", {"class": "third-party"})
        # for ad in third_party_ads:
        #     third_party_ad_id = KijijiAd(ad).id
        #     self.third_party_ads.append(third_party_ad_id)

        # Create a dictionary of all ads with ad id being the key
        for ad in zillow_ads:
            zillow_ad = ZillowAd(ad)

            exclude_flag = 0

            # If any of the ad words match the exclude list then skip
            for x in self.exclude:
                result = re.search(x, str(zillow_ad.info).lower())

                if result is not None:
                    exclude_flag = -1
                    break

            if exclude_flag is not -1:
                if (zillow_ad.id not in self.old_ad_ids and
                        zillow_ad.id not in self.third_party_ads):
                    self.new_ads[zillow_ad.id] = zillow_ad.info
                    self.old_ad_ids.append(zillow_ad.id)

    def get_title(self, soup):
        title_location = soup.find('div', {'class': 'message'})

        if title_location:

            if title_location.find('strong'):
                title = title_location.find('strong')\
                    .text.strip('"').strip(" »").strip("« ")
                return self.format_title(title)

        content = soup.find_all('div', class_='content')
        for i in content:

            if i.find('strong'):
                title = i.find('strong')\
                    .text.strip(' »').strip('« ').strip('"')
                return self.format_title(title)

        return ""

    # Makes the first letter of every word upper-case
    def format_title(self, title):
        new_title = []

        title = title.split()
        for word in title:
            new_word = ''
            new_word += word[0].upper()

            if len(word) > 1:
                new_word += word[1:]

            new_title.append(new_word)

        return ' '.join(new_title)

    # Returns a given list of words to lower-case words
    def words_to_lower(self, words):
        return [word.lower() for word in words]
