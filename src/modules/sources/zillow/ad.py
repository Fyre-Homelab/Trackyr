#!/usr/bin/env python3

class ZillowAd():

    def __init__(self, ad):
        self.title = ad.find('a', {"class": "list-card-addr"}).text.strip()
        self.id = ad['data-listing-id']
        self.ad = ad
        self.info = {}

        self.__locate_info()
        self.__parse_info()

    def __locate_info(self):
        # Locate ad information
        self.info["Title"] = self.ad.find('a', {"class": "list-card-addr"})
        self.info["Image"] = str(self.ad.find('img'))
        self.info["Url"] = self.ad.get("list-card-link")
        self.info["Bedrooms"] =  self.ad.find('div', {"class": "list-card-details"})
        self.info["Bathrooms"] = self.ad.find('div', {"class": "list-card-details"})
        self.info["SquareFootage"] = self.ad.find('div', {"class": "list-card-details"})
        self.info["Price"] = self.ad.find('div', {"class": "list-card-price"})

    def __parse_info(self):
        # Parse Bedrooms and Bathrooms information
        self.info["Bedrooms"] = self.info["Bedrooms"].text.strip() \
            if self.info["Bedrooms"] is not None else ""
        
        self.info["Bathrooms"] = self.info["Bathrooms"].text.strip() \
            if self.info["Bathrooms"] is not None else ""
        
        self.info["SquareFootage"] = self.info["SquareFootage"].text.strip() \
            if self.info["SquareFootage"] is not None else ""

        # Parse remaining ad information
        for key, value in self.info.items():
            if value:
                if key == "Url":
                    self.info[key] = 'http://www.zillow.com' + value

                elif key not in ["Image", "Bedrooms", "Bathrooms", "SquareFootage"]:
                    self.info[key] = value.text.strip()
