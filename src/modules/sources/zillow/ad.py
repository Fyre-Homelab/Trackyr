#!/usr/bin/env python3

import lib.utils.logger as log

class ZillowAd():

    def __init__(self, ad):
        self.title = ad.find('a', {"class": "list-card-link"}).text.strip()
        self.id = ad.find('a', {"class": "list-card-link"}).get('href').split('/')[-2]
        self.ad = ad
        self.info = {}
        self.__locate_info()

    def __locate_info(self):
        # Locate ad information
        self.info["Title"] = self.ad.find('a', {"class": "list-card-link"}).text.strip()
        
        try:
            for link in self.ad.find_all('img'):
                if ".jpg" in link['src']:
                    self.info["Image"] = link['src']
        except:
            self.info["Image"] = ""

        self.info["Url"] = self.ad.find('a', {"class": "list-card-link"}).get('href')
        
        try:
            self.info["Bedrooms"] =  self.ad.find('ul', {"class": "list-card-details"}).select('ul > li')[0].get_text(strip=True)[:-3]
        except:
            pass

        try:
            self.info["Bathrooms"] = self.ad.find('ul', {"class": "list-card-details"}).select('ul > li')[1].get_text(strip=True)[:-2]
        except: 
            pass

        try:
            self.info["SquareFootage"] = self.ad.find('ul', {"class": "list-card-details"}).select('ul > li')[2].get_text(strip=True)[:-4]
        except: 
            pass

        try:
            self.info["Price"] = self.ad.find('div', {"class": "list-card-price"}).text.strip()
        except: 
            pass


