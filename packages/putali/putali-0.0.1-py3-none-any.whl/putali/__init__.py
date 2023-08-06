from usp.tree import sitemap_tree_for_homepage
import requests
import re
import os
import contextlib

class Getallurls:
    def __init__(self,website):
        
        with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
            self.tree = sitemap_tree_for_homepage(website)
        
        self.urls = [page.url for page in self.tree.all_pages()]
    
    def uniqueurls(self):
        return list(set(self.urls))
    
    def usefulurls(self):
        useful_urls = []
        matches = ['.pdf', '.jpeg', '.jpg', '.zip', '.png']
        for url in self.uniqueurls():
            if not any(x in url for x in matches):
                useful_urls.append(url)
        return useful_urls
    
    def emails(self):
        EMAIL_REGEX = r'''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'''
        list_of_emails = set()
        
        urls_to_scrap = self.usefulurls()
        for webpage in urls_to_scrap:
            try:
                r = requests.get(webpage)
                page_source = r.text
                for re_match in re.finditer(EMAIL_REGEX, page_source):
                    list_of_emails.add(re_match.group())
            except:
                continue
        
        return list(list_of_emails)
        
    def phonenumber(self):
        PHONE_REGEX = r'''(?:[\+]?977[- ]?)?9\d{2}-?\d{7}'''
        phone_numbers = set()
        urls_to_scrap = self.usefulurls()
        for webpage in urls_to_scrap:
            try:
                r = requests.get(webpage)
                page_source = r.text
                for re_match in re.finditer(PHONE_REGEX, page_source):
                    phone_numbers.add(re_match.group())
            except:
                continue
        
        return list(phone_numbers)