import requests
from bs4 import BeautifulSoup
import re

__availablecountries__ = ['Nepal', 'USA']

class Scrollhomepage:
    def __init__(self, home_url):
        req = requests.get(home_url)
        soup = BeautifulSoup(req.text, 'html.parser')
        urls_in_homepage = [link.get('href') for link in soup.find_all('a')]
        
        urls_with_rooturl = [x for x in urls_in_homepage if x.startswith(home_url)]
        self.urls_to_scrap = urls_with_rooturl
            
    def emails(self):
        '''Gives out the contact email from the website homepage'''
        EMAIL_REGEX = r'''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'''
        list_of_emails = set()
        
        urls_to_scrap = self.urls_to_scrap
        for webpage in urls_to_scrap:
            try:
                r = requests.get(webpage)
                page_source = r.text
                for re_match in re.finditer(EMAIL_REGEX, page_source):
                    if not re_match.group().startswith('//') and not re_match.group().startswith('www.'):
                        list_of_emails.add(re_match.group())
            except:
                continue
        
        return list(list_of_emails)
    
    def phonenumbers(self, country):
        '''Displays the phone numbers/landline numbers from the website'''
        if country == 'Nepal':
            LANDLINE = r'''(?:[\+]?977[- ]?\d{1,3}[-]\d{5,8})'''
            PHONE_REGEX = r'''(?:[\+]?977[- ]?)?9(8|7|6)\d{1}-?\d{7}'''
            phone_numbers = set()
            urls_to_scrap = self.urls_to_scrap
            for webpage in urls_to_scrap:
                try:
                    r = requests.get(webpage)
                    page_source = r.text
                    for re_match in re.finditer(LANDLINE, page_source):
                        phone_numbers.add(re_match.group())
                    for re_match in re.finditer(PHONE_REGEX, page_source):
                        phone_numbers.add(re_match.group())
                except:
                    continue

            return list(phone_numbers)
        elif country =='USA':
            PHONE_REGEX = r'''^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}'''
            phone_numbers = set()
            urls_to_scrap = self.urls_to_scrap
            for webpage in urls_to_scrap:
                try:
                    r = requests.get(webpage)
                    page_source = r.text
                    for re_match in re.finditer(PHONE_REGEX, page_source):
                        phone_numbers.add(re_match.group())
                except:
                    continue

            return list(phone_numbers)
        else:
            return "The country you entered doesn't match with the available ones. To check the available countries do samparka.__availablecountries__"
            