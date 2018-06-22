#!/usr/bin/env python

import os
import sys
import uuid
import json
import random
import time
import requests
from spylunking.log.setup_logging import build_colorized_logger


useralias = "user1"
if len(sys.argv) > 1:
    useralias = str(sys.argv[1]).lower()

name = "{}-sim".format(useralias)
log = build_colorized_logger(name=name)


def build_request_data(useralias,
                       req_node):
    """build_request_data

    :param useralias: user alias for directory name
    :param req_node: simulated request node
    """

    if "file" not in req_node:
        return None

    use_uniques = req_node["unique_names"]
    use_file = req_node["file"].format(
                    useralias)

    use_data = json.loads(open(use_file, 'r').read())
    if use_uniques:
        if "title" in use_data:
            use_data["title"] = "{}_{}".format(
                use_data["title"],
                str(uuid.uuid4()))
        if "full_file" in use_data:
            use_data["full_file"] = \
                use_data["full_file"].format(
                    str(uuid.uuid4()))
        if "clean_file" in use_data:
            use_data["clean_file"] = \
                use_data["clean_file"].format(
                    str(uuid.uuid4()))
        if "csv_file" in use_data:
            use_data["csv_file"] = \
                use_data["csv_file"].format(
                    str(uuid.uuid4()))
        if "meta_file" in use_data:
            use_data["meta_file"] = \
                use_data["meta_file"].format(
                    str(uuid.uuid4()))
        if "meta_suffix" in use_data:
            use_data["meta_suffix"] = \
                use_data["meta_suffix"].format(
                    str(uuid.uuid4()))
    return use_data
# end of build_request_data


url = os.getenv(
    "ANTINEX_URL",
    "http://localhost:8080")
output_dir = os.getenv(
    "OUTPUT_DIR",
    "/tmp/")

create_user_url = "{}/users/".format(url)
auth_url = "{}/api-token-auth/".format(url)
prepare_url = "{}/mlprepare/".format(url)
ml_job_url = "{}/ml/".format(url)
ml_result_url = "{}/mlresults/".format(url)

user_sim_file = "{}/simulations/sim_{}.json".format(
    os.getcwd(),
    useralias)
if not os.path.exists(user_sim_file):
    log.error(("Failed to find user_sim_file={}")
              .format(user_sim_file))
    sys.exit(1)
# end of checking the path to the user sim json file

sim_data = json.loads(open(user_sim_file, "r").read())
username = sim_data["user"]["username"]
password = sim_data["user"]["password"]
email = sim_data["user"]["email"]

if "unique" in sim_data["user"]:
    username = "{}zzz{}".format(
                username,
                str(uuid.uuid4())[0:16])
    email = "{}zzz{}@email.com".format(
                username,
                str(uuid.uuid4())[0:16])

all_reqs = sim_data["sim_requests"]
stop_on_failure = True
num_loops = 1
if "num_loops" in sim_data:
    num_loops = sim_data["num_loops"]
org_num_reqs = len(all_reqs)
num_reqs = org_num_reqs * num_loops

loop_idx = 1

use_headers = {
    "Content-type": "application/json"
}
jwt_headers = {
    "Content-type": "application/json",
    "Authorization": "JWT {}"
}
auth_headers = {}
create_user_data = {
    "username": username,
    "password": password,
    "email": email
}
login_data = {
    "username": username,
    "password": password
}

jwt_token = None
last_job_id = None
last_result_id = None
last_prepare_id = None
last_cleaned_csv = None
last_cleaned_meta = None
should_sleep = False
req_idx = 1

while loop_idx <= num_loops:

    log.info(("loops={}/{} name={} requests={}")
             .format(
                loop_idx,
                num_loops,
                username,
                num_reqs))

    for org_req_idx, req_node in enumerate(all_reqs):
        try:
            req_idx += 1
            worked = True
            req_name = req_node["name"]
            delay = random.uniform(2.5, 10.9)
            log.info(("{}/{} processing={} "
                      "data={}")
                     .format(
                            req_idx,
                            num_reqs,
                            req_name,
                            req_node))

            use_data = build_request_data(
                            useralias,
                            req_node)

            # by default a failed login will create a user
            if req_name == "login":
                log.info("Login")
                post_response = requests.post(
                    auth_url,
                    data=json.dumps(login_data),
                    headers=use_headers)
                if post_response.status_code != 201 \
                   and post_response.status_code != 200:
                    log.info("Creating User")
                    post_response = requests.post(
                        create_user_url,
                        data=json.dumps(create_user_data),
                        headers=use_headers)
                    if post_response.status_code != 201 \
                       and post_response.status_code != 200:
                        log.error(("Failed to create "
                                   "user={} response={} "
                                   "text={}")
                                  .format(
                                    create_user_data,
                                    post_response.status_code,
                                    post_response.text))
                        sys.exit(1)
                    else:
                        log.info(("Created User={}")
                                 .format(
                                    create_user_data["username"]))
                        post_response = requests.post(
                            auth_url,
                            data=json.dumps(login_data),
                            headers=use_headers)
                    # end of creating a user
                if post_response.status_code != 201 \
                   and post_response.status_code != 200:
                    log.error(("Failed logging in with "
                               "user={} response={} text")
                              .format(
                                    login_data,
                                    post_response.status_code,
                                    post_response.text))
                else:
                    jwt_token = json.loads(
                        post_response.text)["token"]
                    log.info(("user={} token={}")
                             .format(
                                create_user_data["username"],
                                jwt_token))
                    auth_headers = {
                        "Content-type": "application/json",
                        "Authorization": "JWT {}".format(
                            jwt_token)
                    }
                # end of login + create user if necessary
            # end of login
            elif req_name == "prepare":
                log.info("Prepare data={}".format(use_data))
                res = requests.post(
                    prepare_url,
                    data=json.dumps(use_data),
                    headers=auth_headers)
                log.info(("MLPrepare code={} text={}")
                         .format(
                            res.status_code,
                            res.text))
                prepare_record = json.loads(res.text)
                last_prepare_id = prepare_record["id"]
                last_cleaned_csv = prepare_record["clean_file"]
                last_cleaned_meta = "{}cleaned_{}".format(
                    prepare_record["output_dir"],
                    prepare_record["meta_suffix"])

            # end of prepare
            elif req_name == "train":
                use_data["csv_file"] = last_cleaned_csv
                use_data["meta_file"] = last_cleaned_meta
                log.info("Train data={}".format(use_data))
                res = requests.post(
                    ml_job_url,
                    data=json.dumps(use_data),
                    headers=auth_headers)
                log.info(("MLJob code={} text={}")
                         .format(
                            res.status_code,
                            res.text))
                job_record = json.loads(res.text)
                last_job_id = job_record["job"]["id"]
                last_result_id = job_record["results"]["id"]
            # end of train
            elif req_name == "getjob":
                log.info(("Get Job={}")
                         .format(last_job_id))
                res = requests.get(
                    ml_job_url + "{}".format(last_job_id),
                    headers=auth_headers)
                log.info(("MLJob code={} text={}")
                         .format(
                            res.status_code,
                            res.text))
                job_record = json.loads(res.text)
            # end of getjob
            elif req_name == "getjobresult":
                log.info(("Get Job Result={}")
                         .format(
                            last_result_id))
                res = requests.get(
                    ml_result_url + "{}".format(last_result_id),
                    headers=auth_headers)
                log.info(("MLJobResult code={} text={}")
                         .format(
                            res.status_code,
                            res.text))
                result_record = json.loads(res.text)
            # end of getjobresult
            elif req_name == "getprepare":
                log.info(("Get Prepare={}")
                         .format(
                            last_prepare_id))
                res = requests.get(
                    prepare_url + "{}".format(last_prepare_id),
                    headers=auth_headers)
                log.info(("MLPrepare code={} text={}")
                         .format(
                            res.status_code,
                            res.text))
                prepare_record = json.loads(res.text)
            # end of getprepare
            elif req_name == "recentjobs":
                log.info("Recent Jobs")
                res = requests.get(
                    ml_job_url,
                    headers=auth_headers)
                log.info(("MLJob code={} text={}")
                         .format(
                            res.status_code,
                            res.text))
                job_records = json.loads(res.text)
            # end of recentjobs
            elif req_name == "recentresults":
                log.info("Recent Results")
                res = requests.get(
                    ml_result_url,
                    headers=auth_headers)
                log.info(("MLJobResults code={} text={}")
                         .format(
                            res.status_code,
                            res.text))
                result_records = json.loads(res.text)
            # end of recentresults
            elif req_name == "recentprepares":
                log.info("Recent Prepares")
                res = requests.get(
                    prepare_url,
                    headers=auth_headers)
                log.info(("MLPrepares code={} text={}")
                         .format(
                            res.status_code,
                            res.text))
                prepare_records = json.loads(res.text)
            # end of recentprepares
            else:
                log.error(("Not supported simulated request "
                           "{} data={} file={}")
                          .format(
                            req_idx,
                            req_node,
                            user_sim_file))
                worked = False
            # end of supported requests

            if not worked:
                log.error(("{} Failed running "
                           "request={}")
                          .format(
                            req_idx,
                            req_node))
                if stop_on_failure:
                    log.error("Stopping")
                    break
            else:
                if should_sleep:
                    log.info(("simulating sleeping={}")
                             .format(
                                delay))
                    time.sleep(delay)
                else:
                    time.sleep(1.0)
                log.info("success")
                log.info("--------------------------")
        # end of for all
        except Exception as e:
            log.error(("Failed processing "
                       "req={}/{} node={} ex={}")
                      .format(
                        req_idx,
                        num_reqs,
                        req_node,
                        e))
            try_login_again = True
        # end of try/ex
    # end of for all requests
    loop_idx += 1
# end of while

log.info(("Done running simulation "
          "for user={} requests={}")
         .format(
            useralias,
            num_reqs))

sys.exit(0)
