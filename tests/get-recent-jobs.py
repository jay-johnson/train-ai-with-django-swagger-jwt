#!/usr/bin/env python

import os
import sys
import json
import requests
from spylunking.log.setup_logging import build_colorized_logger
from antinex_utils.utils import ppj


name = 'get-recent-jobs'
log = build_colorized_logger(
    name=name)


url = os.getenv(
    "ANTINEX_URL",
    "http://localhost:8010")
username = os.getenv(
    "API_USER",
    "root")
password = os.getenv(
    "API_PASS",
    "123321")

auth_url = "{}/api-token-auth/".format(url)
resource_url = ("{}/ml").format(
                    url)
use_headers = {
    "Content-type": "application/json"
}
login_data = {
    "username": username,
    "password": password
}

# Login as the user:
log.info("Logging in user url={}".format(auth_url))
post_response = requests.post(auth_url,
                              data=json.dumps(login_data),
                              headers=use_headers)

user_token = ""
if post_response.status_code == 200:
    user_token = json.loads(post_response.text)["token"]

if user_token == "":
    log.error(("Failed logging in as user={} - stopping"
               "post_response={}")
              .format(username,
                      post_response.text))
    sys.exit(1)
else:
    log.info(("logged in user={} token={}")
             .format(username,
                     user_token))
# end if/else

log.info("building get data")

use_headers = {
    "Content-type": "application/json",
    "Authorization": "JWT {}".format(user_token)
}

log.info(("Getting Recent Jobs url={}")
         .format(resource_url))
get_response = requests.get(resource_url,
                            headers=use_headers)

if get_response.status_code != 201 \
   and get_response.status_code != 200:
    log.error(("Failed with GET response status={} reason={}")
              .format(get_response.status_code,
                      get_response.reason))
    log.error("Details:\n{}".format(get_response.text))
    sys.exit(1)
else:
    log.info(("SUCCESS - GET Response status={} reason={}")
             .format(get_response.status_code,
                     get_response.reason))

    as_json = True
    record = {}
    if as_json:
        record = json.loads(get_response.text)
        log.info(ppj(record))
# end of get

sys.exit(0)
