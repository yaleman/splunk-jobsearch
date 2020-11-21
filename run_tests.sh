#!/bin/bash

echo "Making data dir"


TESTDIR="./testdata/$(date '+%Y-%m-%d')"
mkdir -p "${TESTDIR}" || exit 1 

echo "Running in test mode, this will write loads of files to ${TESTDIR}"

jobsearch/bin/jsondump.py --write-testfiles 2>"${TESTDIR}/error.log" >"${TESTDIR}/run.log"

if [ -d '/tmp/' ]; then
    mv /tmp/splunk-jobsearch* "${TESTDIR}"
    find "${TESTDIR}" -type f -name 'splunk-jobsearch*' -exec gzip -9 {} \;
else
    echo "Couldn't find /tmp/, you'll need to find the temp dir where python put all the splunk-jobsearch*.txt dump files."
fi