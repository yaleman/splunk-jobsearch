#!/usr/bin/env python
# coding: utf-8

""" pulls a list of the available jobs from the splunk jobs page
    (hopefully they're advertising for less than 2000and returns a json blob for each job
"""

import json
import re
import requests

GET_JOBDATA = True

BASEURL = 'https://www.splunk.com'
JOBSURL = f'{BASEURL}/api/bin/careers/jobs'
params = {
    'keyword' : '',
    'team' : '',
    'region' : '',
    'start' : 0,
    'location' : '',
    'count' : 2000,
}

REGION_OPTIONS = {
    'All' : '',
    'Americas' : 'Americas',
    'APAC' : 'Asia-Pacific',
    'EMEA' : 'Europe and the Middle East',
}

jobpagefinder = re.compile(r'\<script type=\"application\/ld\+json\"\>([^\<]+)\<\/script')
JOBDATA_FIELDS = ['datePosted', 'description', ]

def get_jobdescription(job):
    """ add the job description data to the search """
    joburl = f"{BASEURL}{job.get('url')}"

    jobpage = requests.get(joburl)
    jobpage.raise_for_status()

    jobdata_search = jobpagefinder.findall(jobpage.text)
    if jobdata_search:
        try:
            jobdata = json.loads(jobdata_search[0])
        except json.JSONDecodeError as error:
            # TODO: log this to stderr
            print(f"Error parsing job data JSON ({error}) for {joburl}: {jobdata_search[0]}")

        for field in JOBDATA_FIELDS:
            if field in jobdata:
                job[field] = jobdata.get(field)
    return job

def main():
    """ main loop """
    page = requests.get(JOBSURL)
    page.raise_for_status()

    data = page.json()

    if not data.get('careers'):
        raise ValueError(f"Key careers not found in data: \n {data}")

    for job in data.get('careers'):
        job.pop('allLocations')

        try:
            if GET_JOBDATA:
                job = get_jobdescription(job)
        #pylint: disable=broad-except
        except Exception as error:
            # TODO: log this to stderr
            print("Error grabbing and parsing job data: %s", error)
        print(json.dumps(job))

if __name__ == '__main__':
    main()
