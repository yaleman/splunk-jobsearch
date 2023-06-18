""" pulls a list of the available jobs from the splunk jobs page
    and returns a json blob for each job
    (hopefully they're advertising for less than 2000)
"""
import json
import re
import sys
from datetime import datetime
from typing import Any, Dict

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

def get_jobdescription(job: Dict[str, Any], write_files: bool=False) -> Dict[str, Any]:
    """ add the job description data to the search """
    joburl = f"{BASEURL}{job.get('url')}"

    jobpage = requests.get(joburl, timeout=30)
    if jobpage.status_code == 404:
        print(f"Failed to find job page at {joburl}", file=sys.stderr)
        return job
    jobpage.raise_for_status()
    if write_files:
        write_file(content=jobpage.text)
    jobdata_search = jobpagefinder.findall(jobpage.text)
    if jobdata_search:
        jobdata = jsonfixer(jobdata_search[0], debug=False)
        if jobdata:
            for field in JOBDATA_FIELDS:
                if field in jobdata:
                    job[field] = jobdata.get(field)
        else:
            print("JSON data fix failed, running again with debug on to capture errors", file=sys.stderr)
            jsonfixer(jobdata_search[0], debug=True, write_files=write_files)
    return job

def main(write_files: bool=False) -> bool:
    """ main loop
        if you set write_files, it'll write out the content of all the requests made to ./testdata/%Y-%m-%d/<something>
    """
    try:
        page = requests.get(JOBSURL, timeout=30)
        page.raise_for_status()
        if write_files:
            write_file(content=page.text)
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


    if not data.get('careersList'):
        print(f"Key careersList not found in data: \n {json.dumps(data, indent=4, default=str, ensure_ascii=False)[:500]}, failing", file=sys.stderr)
        return False

    for (jobnum, job) in enumerate(data.get('careersList', [])):
        job.pop('allLocations')
        try:
            if GET_JOBDATA:
                job = get_jobdescription(job, write_files=write_files)
                # add the time field
                job['_time'] = datetime.now().utcnow().isoformat()
                print(f"Parsing job #{jobnum}", file=sys.stderr)
                print(json.dumps(job))
        except Exception as error:
            print(f"Error ({error}) grabbing and parsing job data for job: {json.dumps(job, default=str, ensure_ascii=False)}", file=sys.stderr)
    return True

if __name__ == '__main__':
    if '--write-testfiles' in sys.argv:
        print("Writing debug files", file=sys.stderr)
        main(write_files=True)
    else:
        main()
