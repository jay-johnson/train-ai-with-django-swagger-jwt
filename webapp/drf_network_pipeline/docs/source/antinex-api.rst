Django REST Framework + Celery + JWT + Swagger + Keras + Tensorflow
===================================================================

Automate training AI to defend applications with a Django 2.0+ REST Framework + Celery + Swagger + JWT using Keras and Tensorflow. 

Now supports building the same highly accurate deep neural networks as the `AntiNex Core`_ (**99.8%** accuracy with Django, Flask, React + Redux, Vue and Spring). This repository is fully dockerized and after the django celery worker finishes processing, it will auto-push predictions to the core's celery worker which is decoupled from django and the django database. The core's celery worker stores pre-trained AI neural networks in memory for faster predictions and supports re-training models as needed.

.. _AntiNex Core: https://github.com/jay-johnson/antinex-core#antinex-core

.. image:: https://raw.githubusercontent.com/jay-johnson/train-ai-with-django-swagger-jwt/master/tests/images/django-rest-framework-with-swagger-and-jwt-trains-a-deep-neural-network-using-keras-and-tensorflow-with-83-percent-accuracy.gif

Supported API Requests
----------------------

- `Prepare a Dataset`_
- `Train a Deep Neural Network from a Prepared Dataset using Keras and Tensorflow`_
- `Multi-Tenant Deep Neural Network Training with Simulations`_
- `Get recent Training jobs (including Models as json and weights)`_
- `Get recent Training results (nice for reviewing historical accuracy)`_
- `Get recent Prepared Datasets`_
- `Creating and managing users`_

.. _Prepare a Dataset:  https://github.com/jay-johnson/train-ai-with-django-swagger-jwt#prepare-a-new-dataset-from-captured-recordings
.. _Train a Deep Neural Network from a Prepared Dataset using Keras and Tensorflow: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt#train-a-keras-deep-neural-network-with-tensorflow
.. _Multi-Tenant Deep Neural Network Training with Simulations: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt#multi-tenant-simulations
.. _Get recent Training jobs (including Models as json and weights): https://github.com/jay-johnson/train-ai-with-django-swagger-jwt#get-recent-ml-job-results
.. _Get recent Training results (nice for reviewing historical accuracy): https://github.com/jay-johnson/train-ai-with-django-swagger-jwt#get-recent-ml-jobs
.. _Get recent Prepared Datasets: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt#get-recent-prepared-datasets
.. _Creating and managing users: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt#swagger

This repository was built to help capture ``non-attack`` network traffic and to improve the accuracy of the Keras + Tensorflow Deep Neural Networks by providing them a simple multi-tenant REST API that has Swagger + JWT authentication baked into a single web application. By default, all created Deep Neural Networks are automatically saved as JSON including model weights. It also does not require a database (unless you want to set it up), and will be scaled out with `Celery Connectors`_ in the future. Please refer to the `Network Pipeline`_ repository for more details. This Django application server also comes with a functional Celery worker for running heavyweight, time-intensive tasks required for asynchronous use cases. This is good for when you are trying to train a deep net that takes a few minutes, and you do not want your HTTP client to time out.

.. _Network Pipeline: https://github.com/jay-johnson/network-pipeline
.. _Celery Connectors: https://github.com/jay-johnson/celery-connectors

I plan to automate the tests in a loop and then release the captured HTTP traffic to compile the first ``non-attack`` dataset for pairing up with the OWASP ``attack`` data which is already recorded and available in:

https://github.com/jay-johnson/network-pipeline-datasets

Update: 2018-02-25 - These merged datasets and accuracies are now available in the repository:

https://github.com/jay-johnson/antinex-datasets

Watch Getting Started
=====================

Assuming your host has the pips already cached locally this takes about a minute.

.. raw:: html

    <a href="https://asciinema.org/a/Ct8TS1PMPminXBr5xoojTZq89?autoplay=1" target="_blank"><img src="https://imgur.com/LRVlbcv.png"/></a>

Install
=======

This was tested on Ubuntu 17.10.

::

    git clone https://github.com/jay-johnson/train-ai-with-django-swagger-jwt.git
    cd train-ai-with-django-swagger-jwt
    ./install.sh

Getting Started With Docker
===========================

You can run without these optional steps and just use the default SQLite database. If you want to use docker and download all the containers, you can use the ``compose.yml`` file to start all of the containers and download the latest ``ai-core`` docker image which is ~2.5 GB on disk (built with `Dockerfile`_ and stored on `Docker Hub`_).

.. _Dockerfile: https://github.com/jay-johnson/antinex-core/blob/master/docker/Dockerfile
.. _Docker Hub: https://hub.docker.com/r/jayjohnson/ai-core/

To start all run:

::

    ./run-all.sh

Verify the containers started

::

    docker ps
    CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS              PORTS                    NAMES
    2506f9793c21        jayjohnson/ai-core:latest   "/bin/sh -c 'cd /opt…"   33 seconds ago      Up 33 seconds                                worker
    a9e80d0b16c1        jayjohnson/ai-core:latest   "/bin/sh -c 'cd /opt…"   34 seconds ago      Up 33 seconds                                api
    35611733edd0        jayjohnson/ai-core:latest   "/bin/sh -c 'cd /opt…"   34 seconds ago      Up 33 seconds                                core
    d7f96b5f8882        jayjohnson/ai-core:latest   "/opt/antinex-core/d…"   35 seconds ago      Up 34 seconds                                jupyter
    f344b1cfa5cd        redis:4.0.5-alpine          "docker-entrypoint.s…"   35 seconds ago      Up 34 seconds       0.0.0.0:6379->6379/tcp   redis
    976c31bfbb8c        jayjohnson/pgadmin4:1.0.0   "python ./usr/local/…"   35 seconds ago      Up 34 seconds       0.0.0.0:83->5050/tcp     pgadmin
    f9139346c278        postgres:10.2-alpine        "docker-entrypoint.s…"   35 seconds ago      Up 34 seconds       0.0.0.0:5432->5432/tcp   postgres

Quick links
-----------

If you are running all the containers, you can use these links to move around:

- Use Swagger to Train a new Deep Neural Network (login with ``root`` and ``123321``)

  http://localhost:8080/swagger/#!/ml/ml_create

- Jupyter Notebook showing how the Deep Neural Networks are Trained (login with ``admin`` and ``ALT + r`` to view the slideshow)

  http://localhost:8888/notebooks/AntiNex-Protecting-Django.ipynb

- Jupyter Notebook Slideshow (login with ``admin``)

  http://localhost:8889/Slides-AntiNex-Protecting-Django.slides.html#/

If you are interested in running locally without the large container image, you can run the broker and database stack with docker containers for simulating a more production-ready environment. Here's the containers these steps will start:

#.  Postgres 10
#.  Redis (Pub/Sub, Caching and Celery Tasks)
#.  pgAdmin4 - Web app for managing Postgres

Here's how to run it:

#.  Source the environment

    ::

        source envs/drf-dev.env

#.  Start the Stack

    ::

        ./run-stack.sh 
        Starting stack: full-stack-dev.yml
        Creating postgres ... done
        Creating pgadmin ... 
        Creating postgres ... 

#.  Verify the containers are running

    ::

        docker ps
        CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS              PORTS                                                                                                       NAMES
        2c7cfbd9328e        postgres:10.2-alpine        "docker-entrypoint.s…"   3 minutes ago       Up 3 minutes        0.0.0.0:5432->5432/tcp                                                                                      postgres
        9c34c9588349        jayjohnson/pgadmin4:1.0.0   "python ./usr/local/…"   3 minutes ago       Up 3 minutes        0.0.0.0:83->5050/tcp                                                                                        pgadmin
        75e325113424        redis:4.0.5-alpine          "docker-entrypoint.s…"   3 minutes ago       Up 3 minutes        0.0.0.0:6379->6379/tcp                                                                                      redis

#.  Initialize the Postgres database

    ::

        export USE_ENV=drf-dev
        ./run-migrations.sh

#.  Login to pgAdmin4

    http://localhost:83/browser/

    User: ``admin@email.com``
    Password: ``postgres``

#.  Register the Postgres server

    #.  Right click on "Servers" and then "Create Server"

    #.  On the "General" tab enter a name like "webapp"

    #.  On the "Connection" tab enter:

        Host: postgres

        Username: postgres

        Password: postgres

    #.  Click "Save password?" check box

    #.  Click the "Save" button

    #.  Navigate down the tree:

        Servers > webapp (or the name you entered) > Databases > webapp > Schemas > public > Tables

    #.  Confirm there's database tables with names like:

        ::

            pipeline_mljob
            pipeline_mljobresult
            pipeline_mlprepare

Start
=====

By default, this project uses `gunicorn`_ to start, but you can change to `uwsgi`_ by running ``export APP_SERVER=uwsgi`` before starting. Both app servers should work just fine.

Note: if you are running the docker "full stack" please make sure to run: ``export USE_ENV=drf-dev`` before starting the django application, or you can use ``run-django.sh`` which should do the same as ``start.sh``.

::

    ./start.sh

    Starting Django listening on TCP port 8080
    http://localhost:8080/swagger

    [2018-02-07 11:27:20 -0800] [10418] [INFO] Starting gunicorn 19.7.1
    [2018-02-07 11:27:20 -0800] [10418] [INFO] Listening at: http://127.0.0.1:8080 (10418)
    [2018-02-07 11:27:20 -0800] [10418] [INFO] Using worker: sync
    [2018-02-07 11:27:20 -0800] [10418] [INFO] DJANGO_DEBUG=yes - auto-reload enabled
    [2018-02-07 11:27:20 -0800] [10418] [INFO] Server is ready. Spawning workers
    [2018-02-07 11:27:20 -0800] [10422] [INFO] Booting worker with pid: 10422
    [2018-02-07 11:27:20 -0800] [10422] [INFO] Worker spawned (pid: 10422)
    [2018-02-07 11:27:20 -0800] [10423] [INFO] Booting worker with pid: 10423
    [2018-02-07 11:27:20 -0800] [10423] [INFO] Worker spawned (pid: 10423)
    [2018-02-07 11:27:20 -0800] [10424] [INFO] Booting worker with pid: 10424
    [2018-02-07 11:27:20 -0800] [10424] [INFO] Worker spawned (pid: 10424)
    [2018-02-07 11:27:20 -0800] [10426] [INFO] Booting worker with pid: 10426
    [2018-02-07 11:27:20 -0800] [10426] [INFO] Worker spawned (pid: 10426)
    [2018-02-07 11:27:20 -0800] [10430] [INFO] Booting worker with pid: 10430
    [2018-02-07 11:27:20 -0800] [10430] [INFO] Worker spawned (pid: 10430)

.. _gunicorn: http://docs.gunicorn.org/
.. _uwsgi: https://uwsgi-docs.readthedocs.io/en/latest/

Celery Worker
=============

Start the Worker
----------------

Start the Celery worker in a new terminal to process published Django work tasks for heavyweight, time-intensive operations.

::

    ./run-worker.sh

Verify the Celery Worker Processes a Task without Django
--------------------------------------------------------

I find the first time I integrate Celery + Django + Redis can be painful. So I try to validate Celery tasks work before connecting Celery to Django over a message broker (like Redis). Here is a test tool for helping debug this integration with the `celery-loaders`_ project. It's also nice not having to click through the browser to debug a new task.

#.  Run the task test script

    ::

        ./run-celery-task.py -t drf_network_pipeline.users.tasks.task_get_user -f tests/celery/task_get_user.json
        2018-02-25 23:25:03,832 - run-celery-task - INFO - start - run-celery-task
        2018-02-25 23:25:03,832 - run-celery-task - INFO - connecting Celery=run-celery-task broker=redis://localhost:6379/9 backend=redis://localhost:6379/10 tasks=['drf_network_pipeline.users.tasks']
        2018-02-25 23:25:03,832 - get_celery_app - INFO - creating celery app=run-celery-task tasks=['drf_network_pipeline.users.tasks']
        2018-02-25 23:25:03,847 - run-celery-task - INFO - app.broker_url=redis://localhost:6379/9 calling task=drf_network_pipeline.users.tasks.task_get_user data={'user_id': 1}
        2018-02-25 23:25:03,897 - run-celery-task - INFO - calling task=drf_network_pipeline.users.tasks.task_get_user - started job_id=72148f73-9b3f-4d15-9a95-70be7fbd3f71
        2018-02-25 23:25:03,905 - run-celery-task - INFO - calling task=drf_network_pipeline.users.tasks.task_get_user - success job_id=72148f73-9b3f-4d15-9a95-70be7fbd3f71 task_result={'id': 1, 'username': 'root', 'email': 'root@email.com'}
        2018-02-25 23:25:03,905 - run-celery-task - INFO - end - run-celery-task

#.  Verify the Celery Worker Processed the Task

    If Redis and Celery are working as expected, the logs should print something similar to the following:

    ::

        2018-02-26 07:25:03,897 - celery.worker.strategy - INFO - Received task: drf_network_pipeline.users.tasks.task_get_user[72148f73-9b3f-4d15-9a95-70be7fbd3f71]  
        2018-02-26 07:25:03,898 - user_tasks - INFO - task - task_get_user - start user_data={'user_id': 1}
        2018-02-26 07:25:03,899 - user_tasks - INFO - finding user=1
        2018-02-26 07:25:03,903 - user_tasks - INFO - found user.id=1 name=root
        2018-02-26 07:25:03,904 - user_tasks - INFO - task - task_get_user - done
        2018-02-26 07:25:03,905 - celery.app.trace - INFO - Task drf_network_pipeline.users.tasks.task_get_user[72148f73-9b3f-4d15-9a95-70be7fbd3f71] succeeded in 0.006255952997889835s: {'id': 1, 'username': 'root', 'email': 'root@email.com'}

.. _celery-loaders: https://github.com/jay-johnson/celery-loaders

Automation
==========

All of these scripts run in the ``tests`` directory:

::

    cd tests

Make sure the virtual environment has been loaded:

::

    source ~/.venvs/venvdrfpipeline/bin/activate

Clone the datasets repository
-----------------------------

git clone https://github.com/jay-johnson/network-pipeline-datasets /opt/datasets

Prepare a new Dataset from Captured Recordings
----------------------------------------------

::

    ./build-new-dataset.py

.. raw:: html

    <a href="https://asciinema.org/a/Py5OaIFOJJIMCdP5Ktjd0VhOu?autoplay=1" target="_blank"><img src="https://asciinema.org/a/Py5OaIFOJJIMCdP5Ktjd0VhOu.png"/></a>

Train a Keras Deep Neural Network with Tensorflow
-------------------------------------------------

::

    create-keras-dnn.py

    ...

    2018-02-03 00:31:24,342 - create-keras-dnn - INFO - SUCCESS - Post Response status=200 reason=OK
    2018-02-03 00:31:24,342 - create-keras-dnn - INFO - {'job': {'id': 1, 'user_id': 1, 'user_name': 'root', 'title': 'Keras DNN - network-pipeline==1.0.9', 'desc': 'Tensorflow backend with simulated data', 'ds_name': 'cleaned', 'algo_name': 'dnn', 'ml_type': 'keras', 'status': 'initial', 'control_state': 'active', 'predict_feature': 'label_value', 'training_data': {}, 'pre_proc': {}, 'post_proc': {}, 'meta_data': {}, 'tracking_id': 'ml_701552d5-c761-4c69-9258-00d05ff81a48', 'version': 1, 'created': '2018-02-03 08:31:17', 'updated': '2018-02-03 08:31:17', 'deleted': ''}, 'results': {'id': 1, 'user_id': 1, 'user_name': 'root', 'job_id': 1, 'status': 'finished', 'version': 1, 'acc_data': {'accuracy': 83.7837837300859}, 'error_data': None, 'created': '2018-02-03 08:31:24', 'updated': '2018-02-03 08:31:24', 'deleted': ''}}

.. raw:: html

    <a href="https://asciinema.org/a/FdtNSkcRK7VFktg5NGVAQA1In?autoplay=1" target="_blank"><img src="https://asciinema.org/a/FdtNSkcRK7VFktg5NGVAQA1In.png"/></a>

Create a Highly Accurate Deep Neural Network for Protecting Django
------------------------------------------------------------------

This is the same API request the core uses to build the Django DNN with an accuracy of **99.8%**:

https://github.com/jay-johnson/antinex-core#accuracy-and-prediction-report

with Notebook:

https://github.com/jay-johnson/antinex-core/blob/master/docker/notebooks/AntiNex-Protecting-Django.ipynb

::

    ./create-keras-dnn.py -f ./scaler-full-django-antinex-simple.json 

    Please wait... this can take a few minutes

    ...

    2018-03-21 06:04:48,314 - ml_tasks - INFO - saving job=83 results
    2018-03-21 06:04:50,387 - ml_tasks - INFO - updating job=83 results=83
    2018-03-21 06:04:53,957 - ml_tasks - INFO - task - ml_job - done - ml_job.id=83 ml_result.id=83 accuracy=99.81788079470199 predictions=30200

Train and Predict with just a Dictionary List of Records
--------------------------------------------------------

This will send a list of records to the API to train and make predictions. This mimics the live-prediction capability in the core for reusing pre-trained DNNs to make predictions faster. I use it to send the newest records to predict, so I do not have to generate lots of csv files everywhere + all-the-time.

::

    ./create-keras-dnn.py -f ./predict-rows-scaler-full-django.json 

Get a Prepared Dataset
----------------------

::

    export PREPARE_JOB_ID=1
    ./get-a-prepared-dataset.py

.. raw:: html

    <a href="https://asciinema.org/a/J0xedsJx5dJ1Z1LYPI2is7SjB?autoplay=1" target="_blank"><img src="https://asciinema.org/a/J0xedsJx5dJ1Z1LYPI2is7SjB.png"/></a>

Get an ML Job
-------------

Any trained Keras Deep Neural Network models are saved as an ``ML Job``.

::

    export JOB_ID=1
    ./get-a-job.py

.. raw:: html

    <a href="https://asciinema.org/a/A8fJs0okBxltJDI2X1uTghddz?autoplay=1" target="_blank"><img src="https://imgur.com/gFsh5q8.png"/></a>

Get an ML Job Result
--------------------

::

    export JOB_RESULT_ID=1
    ./get-a-result.py

.. raw:: html

    <a href="https://asciinema.org/a/3nE0kab7oVyFIOAywQqM7BPyZ?autoplay=1" target="_blank"><img src="https://asciinema.org/a/3nE0kab7oVyFIOAywQqM7BPyZ.png"/></a>

Get Recent Prepared Datasets
----------------------------

::

    ./get-recent-datasets.py

.. raw:: html

    <a href="https://asciinema.org/a/9O32uMMCj9NmTLuYqFoyIE1rk?autoplay=1" target="_blank"><img src="https://asciinema.org/a/9O32uMMCj9NmTLuYqFoyIE1rk.png"/></a>

Get Recent ML Jobs
------------------

::

    ./get-recent-jobs.py

.. raw:: html

    <a href="https://asciinema.org/a/7TBpEj757q4crNHCDASlChWn2?autoplay=1" target="_blank"><img src="https://asciinema.org/a/7TBpEj757q4crNHCDASlChWn2.png"/></a>


Get Recent ML Job Results
-------------------------

This is nice for reviewing historical accuracy as your tune your models.

::

    ./get-recent-results.py

.. raw:: html

    <a href="https://asciinema.org/a/TTjDnqc65voanvFq4HUxJ142k?autoplay=1" target="_blank"><img src="https://asciinema.org/a/TTjDnqc65voanvFq4HUxJ142k.png"/></a>

Advanced Naming for Multi-Tenant Environments
=============================================

Problems will happen if multiple users are sharing the same host's ``/tmp/`` directory with the default naming conventions. To prevent issues, it is recommended to change the output dataset directory to separate directories per user and to make sure the directories are accessible by the Django server processes. Here's an example of changing the output directory to my user which triggers the custom name detection. This detection means I will see logs for the training command to run with my newly generated dataset and metadata files:

::

    mkdir /opt/jay
    export OUTPUT_DIR=/opt/jay/
    ./build-new-dataset.py

    ...

    Train a Neural Network with:
    ./create-keras-dnn.py /opt/jay/cleaned_attack_scans.csv /opt/jay/cleaned_metadata.json

If changing the output directory is not possible, then users will need to make sure the file names are unique before running. Here's an example naming strategy for the csv datasets and metadata files to prevent collisions. The ``build-new-dataset.py`` script will also suggest the training command to run when you activate custom names:

Prepare a Named Dataset
-----------------------

::

    ./build-new-dataset.py /tmp/<MyFirstName>_$(date +"%Y-%m-%d-%H-%m-%N")_full.csv /tmp/<MyFirstName>_$(date +"%Y-%m-%d-%H-%m-%N")_readytouse.csv

Example that shows the suggested training command to run using the named dataset files on disk:

::

    ./build-new-dataset.py /tmp/jay_$(date +"%Y-%m-%d-%H-%m-%N")_full.csv /tmp/jay_$(date +"%Y-%m-%d-%H-%m-%N")_readytouse.csv

    ...

    Train a Neural Network with:
    ./create-keras-dnn.py /tmp/jay_2018-02-05-21-02-274468596_readytouse.csv /tmp/cleaned_meta-54525d8da8a54e9d9005a29c63f2918b.json

Confirm the files were created:

::

    ls -lrth /tmp/jay_2018-02-05-21-02-274468596_readytouse.csv /tmp/cleaned_meta-54525d8da8a54e9d9005a29c63f2918b.json
    -rw-rw-r-- 1 jay jay 143K Feb  5 21:23 /tmp/jay_2018-02-05-21-02-274468596_readytouse.csv
    -rw-rw-r-- 1 jay jay 1.8K Feb  5 21:23 /tmp/cleaned_meta-54525d8da8a54e9d9005a29c63f2918b.json

Please note, if you use filenames and set the ``OUTPUT_DIR`` environment variable, the environment variable takes priority (even if you specify ``/path/to/some/dir/uniquename.csv``). The dataset and metadata files will be stored in the ``OUTPUT_DIR`` directory:

::

    echo $OUTPUT_DIR
    /opt/jay/

    ./build-new-dataset.py jay_$(date +"%Y-%m-%d-%H-%m-%N")_full.csv jay_$(date +"%Y-%m-%d-%H-%m-%N")_readytouse.csv

    ...

    Train a Neural Network with:
    ./create-keras-dnn.py /opt/jay/jay_2018-02-05-22-02-521671337_readytouse.csv /opt/jay/cleaned_meta-2b961845162a4d6e9e382c6f540302fe.json

Swagger
=======

Create a User
-------------

http://localhost:8080/swagger/#!/users/users_create

Click on the yellow ``Example Value`` section to paste in defaults or paste in your version of:

::

    {
        "username": "test",
        "password": "123321",
        "email": "your@email.com"
    }

Login User
----------

If you want to login as the super user:

- Username: ``root``
- Password: ``123321``

http://localhost:8080/api-auth/login/

Logout User
-----------

http://localhost:8080/swagger/?next=/swagger/#!/accounts/accounts_logout_create

JWT
===

Get a Token
-----------

This will validate authentication with JWT is working:

::

    ./get_user_jwt_token.sh 
    {"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0LCJ1c2VybmFtZSI6InJvb3QiLCJleHAiOjE1MTc1OTg3NTIsImVtYWlsIjoicm9vdEBlbWFpbC5jb20ifQ.ip3Lj5o4SCK4TARlDuLyw-Dc6qMkt8xUx8WsQwIn2uo"}

(Optional) If you have ``jq`` installed:

::

    ./get_user_jwt_token.sh | jq
    {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0LCJ1c2VybmFtZSI6InJvb3QiLCJleHAiOjE1MTc1OTg3NDEsImVtYWlsIjoicm9vdEBlbWFpbC5jb20ifQ.WAIatDGkeFJbH6LL_4rRQaAydZXcE8j0KK7dBnA2GJU"
    }

http://localhost:8080/swagger/?next=/swagger/#!/ml/ml_run_create

Development
===========

Swagger Prepare a new Dataset from Captured Recordings
------------------------------------------------------

http://localhost:8080/swagger/#!/mlprepare/mlprepare_create

Paste in the following values and click **Try it Out**:

::

    {
        "title": "Prepare new Dataset from recordings",
        "desc": "",
        "ds_name": "new_recording",
        "full_file": "/tmp/fulldata_attack_scans.csv",
        "clean_file": "/tmp/cleaned_attack_scans.csv",
        "meta_suffix": "metadata.json",
        "output_dir": "/tmp/",
        "ds_dir": "/opt/datasets",
        "ds_glob_path": "/opt/datasets/*/*.csv",
        "pipeline_files": {
            "attack_files": []
        },
        "meta_data": {},
        "post_proc": {
            "drop_columns": [
                "src_file",
                "raw_id",
                "raw_load",
                "raw_hex_load",
                "raw_hex_field_load",
                "pad_load",
                "eth_dst",
                "eth_src",
                "ip_dst",
                "ip_src"
            ],
            "predict_feature": "label_name"
        },
        "label_rules": {
            "set_if_above": 85,
            "labels": [
                "not_attack",
                "attack"
            ],
            "label_values": [
                0,
                1
            ]
        },
        "version": 1
    }

Swagger Train a Keras Deep Neural Network with Tensorflow
---------------------------------------------------------

http://0.0.0.0:8080/swagger/#!/ml/ml_create

Paste in the following values and click **Try it Out**:

#.  Build the Django DNN for Predicting Network Attacks

    ::

        {
            "label": "Full-Django-AntiNex-Simple-Scaler-DNN",
            "dataset": "/opt/antinex-datasets/v1/webapps/django/training-ready/v1_django_cleaned.csv",
            "ml_type": "classification",
            "predict_feature": "label_value",
            "features_to_process": [
                <list of comma separated column names>
            ],
            "ignore_features": [
                <optional list of comma separated column names>
            ],
            "sort_values": [
                <optional list of comma separated column names>
            ],
            "seed": 42,
            "test_size": 0.2,
            "batch_size": 32,
            "epochs": 15,
            "num_splits": 2,
            "loss": "binary_crossentropy",
            "optimizer": "adam",
            "metrics": [
                "accuracy"
            ],
            "histories": [
                "val_loss",
                "val_acc",
                "loss",
                "acc"
            ],
            "model_desc": {
                "layers": [
                    {
                        "num_neurons": 200,
                        "init": "uniform",
                        "activation": "relu"
                    },
                    {
                        "num_neurons": 1,
                        "init": "uniform",
                        "activation": "sigmoid"
                    }
                ]
            },
            "label_rules": {
                "labels": [
                    "not_attack",
                    "not_attack",
                    "attack"
                ],
                "label_values": [
                    -1,
                    0,
                    1
                ]
            },
            "version": 1
        }

#.  Prototyping with a List of Records

    I use this script to convert a configurable number of records from the bottom of a csv file which helps build these type of prediction json files:

    https://github.com/jay-johnson/antinex-core/blob/master/antinex_core/scripts/convert-bottom-rows-to-json.py

    ::

         ./create-keras-dnn.py -f ./readme-predict-demo-1.json 

    Here are the contents of ``./tests/readme-predict-demo-1.json``

    ::

        {
            "label": "Prediction-Model-Prototyping",
            "predict_rows": [
                {
                    "_dataset_index": 1,
                    "label_value": 1,
                    "more_keys": 54.0
                },
                {
                    "_dataset_index": 2,
                    "label_value": 1,
                    "more_keys": 24.0
                },
                {
                    "_dataset_index": 2,
                    "label_value": 0,
                    "more_keys": 33.0
                }
            ],
            "ml_type": "classification",
            "predict_feature": "label_value",
            "features_to_process": [
                "more_keys"
            ],
            "ignore_features": [
            ],
            "sort_values": [
            ],
            "seed": 42,
            "test_size": 0.2,
            "batch_size": 32,
            "epochs": 15,
            "num_splits": 2,
            "loss": "binary_crossentropy",
            "optimizer": "adam",
            "metrics": [
                "accuracy"
            ],
            "histories": [
                "val_loss",
                "val_acc",
                "loss",
                "acc"
            ],
            "model_desc": {
                "layers": [
                    {
                        "num_neurons": 200,
                        "init": "uniform",
                        "activation": "relu"
                    },
                    {
                        "num_neurons": 1,
                        "init": "uniform",
                        "activation": "sigmoid"
                    }
                ]
            },
            "label_rules": {
                "labels": [
                    "not_attack",
                    "not_attack",
                    "attack"
                ],
                "label_values": [
                    -1,
                    0,
                    1
                ]
            },
            "version": 1
        }


#.  Deprecated - Using just CSV files

    ::

        {
            "csv_file": "/tmp/cleaned_attack_scans.csv",
            "meta_file": "/tmp/cleaned_metadata.json",
            "title": "Keras DNN - network-pipeline==1.0.9",
            "desc": "Tensorflow backend with simulated data",
            "ds_name": "cleaned",
            "algo_name": "dnn",
            "ml_type": "keras",
            "predict_feature": "label_value",
            "training_data": "{}",
            "pre_proc": "{}",
            "post_proc": "{}",
            "meta_data": "{}",
            "version": 1
        }

Run Tests
---------

The unit tests can be run:

::

    ./run-tests.sh

    ...

    PASSED - unit tests

Or run a single test

::

    source envs/dev.env; cd webapp; source ~/.venvs/venvdrfpipeline/bin/activate
    python manage.py test drf_network_pipeline.tests.test_ml.MLJobTest

Multi-Tenant Simulations
========================

Simulations run from the ``./tests/`` directory.

::

    cd tests


Run the default ``user1`` simulation in a new terminal:

::

    ./run-user-sim.py

In a new terminal start ``user2`` simulation:

::

    ./run-user-sim.py user2

In a new terminal start ``user3`` simulation:

::

    ./run-user-sim.py user3

Want to check how many threads each process is using?
-----------------------------------------------------

It appears that either Keras or Tensorflow are using quite a bit of threads behind the scenes. On Ubuntu you can view the number of threads used by ``gunicorn`` or ``uwsgi`` with these commands:

::

    ps -o nlwp $(ps awuwx | grep django | grep -v grep | awk '{print $2}')

If you're running ``uwsgi`` instead of the ``gunicorn`` use:

::

    ps -o nlwp $(ps awuwx | grep uwsgi | grep -v grep | awk '{print $2}')

Stop Full Stack
===============

If you are running the "full stack", then you can run this command to stop the docker containers:

::

    ./stop-stack.sh 

Testing
-------

#.  Set up the Testing Runtime and Environment Variables

    ::

        source ~/.venvs/venvdrfpipeline/bin/activate
        source ./envs/dev.env

#.  Change to the ``webapp`` directory

    Tests need to run in the same directory as the ``manage.py``

    ::

        cd webapp

#.  Run all Tests

    ::

        python manage.py test

#.  Run all Test Cases in a Test module

    ::

        python manage.py test drf_network_pipeline.tests.test_ml

#.  Run a Single Test Case

    ::
        
        python manage.py test drf_network_pipeline.tests.test_ml.MLJobTest.test_ml_predict_helper_works

    or

    ::

        python manage.py test drf_network_pipeline.tests.test_user.AccountsTest.test_create_user_with_invalid_email

Linting
-------

flake8 .

pycodestyle --exclude=.tox,.eggs,migrations

License
-------

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/master/LICENSE

Citations and Included Works
============================

Special thanks to these amazing projects for helping make this easier!

Original Django project template from
-------------------------------------
https://github.com/jpadilla/django-project-template

Django REST Framework
---------------------
https://github.com/encode/django-rest-framework

Celery
------

http://www.celeryproject.org/

User Registration
-----------------
https://github.com/szopu/django-rest-registration

Swagger for Django
------------------
https://github.com/marcgibbons/django-rest-swagger

JWT for Django REST
-------------------
https://github.com/GetBlimp/django-rest-framework-jwt

Keras
-----
https://github.com/keras-team/keras

Tensorflow
----------
https://github.com/tensorflow

SQLite
------
https://www.sqlite.org/index.html

Gunicorn
--------

http://docs.gunicorn.org/

uWSGI
-----

https://uwsgi-docs.readthedocs.io/en/latest/

pgAdmin
-------

https://www.pgadmin.org/

PostgreSQL
----------

https://www.postgresql.org/

Django Cacheops
---------------

https://github.com/Suor/django-cacheops
