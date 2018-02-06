#!/usr/bin/env python

import os
import sys
import logging
import uuid
import json
import requests
from network_pipeline.log.setup_logging import setup_logging


setup_logging(config_name="logging.json")
name = "build-new-ds"
log = logging.getLogger(name)


test_data_file = os.getenv(
    "TEST_DATA",
    "./prepare-new-dataset.json")
url = os.getenv(
    "BASE_URL",
    "http://localhost:8080")
username = os.getenv(
    "API_USER",
    "root")
password = os.getenv(
    "API_PASS",
    "123321")
output_dir = os.getenv(
    "OUTPUT_DIR",
    "/tmp/")

if not os.path.exists(test_data_file):
    log.info(("Failed to find test_data_file={}")
             .format(test_data_file))
    sys.exit(1)
# end of checking the path to the test json file

using_named_files = False
custom_output_dir = False
test_data = json.loads(open(test_data_file, "r").read())
test_data["output_dir"] = output_dir
if test_data["output_dir"][-1] != "/":
    test_data["output_dir"] += "/"
if len(sys.argv) > 2:
    full_file = str(sys.argv[1])
    clean_file = str(sys.argv[2])
    test_data["full_file"] = full_file
    test_data["clean_file"] = clean_file
    test_data["meta_suffix"] = "meta-{}.json".format(
        str(uuid.uuid4()).replace("-", ""))
    using_named_files = True
# end of full + clean file custom args

if len(sys.argv) > 3:
    meta_suffix = str(sys.argv[3])
    test_data["meta_suffix"] = meta_suffix
# end of meta_suffix parsing

# allow changing the output dir when
# not in custom naming mode
if "/tmp" not in test_data["output_dir"]:
    test_data["full_file"] = ("{}{}").format(
        output_dir,
        test_data["full_file"].split("/")[-1])
    test_data["clean_file"] = ("{}{}").format(
        output_dir,
        test_data["clean_file"].split("/")[-1])
    custom_output_dir = True
# end of setting a custom output dir

auth_url = "{}/api-token-auth/".format(url)
resource_url = "{}/mlprepare/".format(url)
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

log.info("building post data")

use_headers = {
    "Content-type": "application/json",
    "Authorization": "JWT {}".format(user_token)
}

log.info(("Running ML Job url={} "
          "test_data={}")
         .format(resource_url,
                 test_data))
post_response = requests.post(resource_url,
                              data=json.dumps(test_data),
                              headers=use_headers)

if post_response.status_code != 201 \
   and post_response.status_code != 200:
    log.error(("Failed with Post response status={} reason={}")
              .format(post_response.status_code,
                      post_response.reason))
    log.error("Details:\n{}".format(post_response.text))
    sys.exit(1)
else:
    log.info(("SUCCESS - Post Response status={} reason={}")
             .format(post_response.status_code,
                     post_response.reason))

    as_json = True
    record = {}
    if as_json:
        record = json.loads(post_response.text)
        log.info(record)
    if using_named_files or custom_output_dir:
        print("")
        print("Train a Neural Network with:")
        print(("./create-keras-dnn.py "
               "{} {}cleaned_{}").format(
                    record["clean_file"],
                    record["output_dir"],
                    record["meta_suffix"]))
        print("")
# end of post for running an ML Job

sys.exit(0)
