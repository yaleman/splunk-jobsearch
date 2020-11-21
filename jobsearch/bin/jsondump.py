#!/usr/bin/env python
# coding: utf-8

""" pulls a list of the available jobs from the splunk jobs page
    (hopefully they're advertising for less than 2000and returns a json blob for each job
"""


import json
import re
import sys
import time
from datetime import datetime
from hashlib import md5

import requests

from utilities.jsonfixer import jsonfixer 
from utilities.filewriter import write_file
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

def get_jobdescription(job, write_files: bool=False):
    """ add the job description data to the search """
    joburl = f"{BASEURL}{job.get('url')}"

    jobpage = requests.get(joburl)
    if jobpage.status_code == 404:
        return job
    jobpage.raise_for_status()
    if write_files:
        # make hash of url for file storage
        urlhash = md5(joburl.encode('utf-8'))
        if not write_file(filename=f"jobdescription-{urlhash.hexdigest()}", content=jobpage.text):
            sys.exit()

    jobdata_search = jobpagefinder.findall(jobpage.text)
    if jobdata_search:
        jobdata = jsonfixer(jobdata_search[0], debug=False)
        if jobdata:
            for field in JOBDATA_FIELDS:
                if field in jobdata:
                    job[field] = jobdata.get(field)
        else:
            print("JSON data fix failed, running again with debug on to capture errors", file=sys.stderr)
            jsonfixer(jobdata_search[0], debug=True)
    return job

def main(write_files: bool=False):
    """ main loop 
    
        if you set write_files, it'll write out the content of all the requests made to ./testdata/%Y-%m-%d/<something>
    """
    try:
        page = requests.get(JOBSURL)
    
        page.raise_for_status()
        if write_files:
            # make hash of url for file storage
            urlhash = md5(JOBSURL.encode('utf-8'))
            if not write_file(filename=f"jobspage-{urlhash.hexdigest()}.txt", content=page.text):
                sys.exit()

    except Exception as error_message:
        print(f"Failed to query job data from {JOBSURL}: {error_message}", file=sys.stderr)
        return False
    
    try:
        data = page.json()
    except json.JSONDecodeError as json_error:
        print(f"Failed to parse {JOBSURL} into JSON: {json_error}", file=sys.stderr)
        return False
    except Exception as error_message:
        print(f"Failed to turn {JOBSURL} into JSON: {error_message}", file=sys.stderr)
        return False


    if not data.get('careers'):
        print(f"Key careers not found in data: \n {data}, failing", file=sys.stderr)
        return False

    jobnum = 0
    for job in data.get('careers'):
        job.pop('allLocations')

        try:
            if GET_JOBDATA:
                job = get_jobdescription(job, write_files=write_files)
                # add the time field
                job['_time'] = datetime.now().utcnow().isoformat()
                print(f"Parsing job #{jobnum}", file=sys.stderr)
                jobnum = jobnum + 1
                print(json.dumps(job))
        except Exception as error:
            print(f"Error ({error}) grabbing and parsing job data for job: {json.dumps(job)}", file=sys.stderr)

if __name__ == '__main__':
    if '--write-testfiles' in sys.argv:
        main(write_files=True)
    else:
        main()
