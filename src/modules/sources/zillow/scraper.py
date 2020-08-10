#!/usr/bin/env python3

import  os
import requests
from bs4 import BeautifulSoup
import json

from pathlib import Path
import re
from modules.sources.zillow.ad import ZillowAd

import lib.utils.logger as log

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
        log.info_print(f"url 1: {url}")
        while url:
            # Get the html data from the URL
            req_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.8',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
            }

            page = requests.get(url, headers=req_headers)
            soup = BeautifulSoup(page.content, "html.parser")

            # If the title doesnt exist pull it from the html data
            if title is None:
                title = self.get_title(soup)

            # Find ads on the page
            self.find_ads(soup)

            # Set url for next page of ads
            url = soup.find('a', {'title': 'Next page'})
            disabled = True
            try:
                disabled_state = url['disabled']
            except:
                disabled = False

            if url:
                if disabled:
                    log.info_print(f"if disabled: {disabled}")
                    break
                else:
                    url = 'https://www.zillow.com' + url['href']
                    log.info_print(f"new url: {url}")
        return self.new_ads, title

    def find_ads(self, soup):
        # Finds all ad trees in page html.
        zillow_ads = soup.find_all("article", {"class": "list-card list-card_not-saved"})

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
