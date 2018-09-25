#!/usr/bin/env python
# coding: utf-8

""" pulls a list of the available jobs from the splunk jobs page (hopefully they're advertising for less than 2000and returns a json blob for each job """

import requests
from bs4 import BeautifulSoup
from json import dumps

url = 'https://splunk.jobs/jobs/ajax/joblisting/?num_items=2000'

def stripit(string, pairs):
    for start, end in pairs:
        while start in string:
            string = string.replace(start, end)
    return string

page = requests.get(url)
soup = BeautifulSoup(page.text, 'lxml')
jobli = soup.select('li[class="direct_joblisting with_description"]')

jobs = {}
for job in jobli:
    title = job.find('h4').contents[0].text
    title_link = job.find_all('a', href=True)[0]['href']

    location = job.select('div[class="direct_joblocation"]')[0].text
    location = stripit(location, [
        ('\n', ''),
        ("\t", ' '),
        ('  ', ' '),
    ])
    try:
        city, region = location.split(",")
        region = region.strip()
    except ValueError:
        #print("Couldn't split this: '{}'".format(location))
        #print("Full job:\n{}".format(job.text))
        #exit()
        city = ''
        region = location.strip()
    print(dumps({'title' : title, 'title_link' : title_link, 'city' : city, 'region' : region}))
