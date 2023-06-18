#!/bin/bash

set -e

APP_DIR="jobsearch"

poetry run find "${APP_DIR}/" -type f -name '*.conf' -exec ksconf check {} \;

echo "Creating ${APP_DIR}.tgz"

find . -type d -name __pycache__ -delete
COPYFILE_DISABLE=1 tar czf "${APP_DIR}.tgz" --exclude '*/__pycache__/*' "${APP_DIR}/"

echo "Done!"