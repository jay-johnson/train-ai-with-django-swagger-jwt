.. AntiNex - Deep Neural Networks for Defense documentation master file, created by
   sphinx-quickstart on Wed Mar 28 12:37:48 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

AntiNex Docs
============

Helping everyone use Deep Neural Networks for Defense
-----------------------------------------------------

.. image:: https://imgur.com/pEEnUZT.png
    :alt: AntiNex - Helping everyone use Deep Neural Networks for Defense

What is this?
=============

AntiNex is a free tool for helping anyone defend against software attacks. It helps users train highly accurate Deep Neural Networks (dnn's) from specialized datasets. These datasets are captured network traffic packets in the OSI layers 2, 3, 4 and 5. Once labeled as attack and non-attack records, you can use your dnn's for identifying attack records across the network. With this approach, AntiNex can predict attacks on web applications like: Django, Flask, React and Redux, Vue, and Spring with repeatable accuracies above **99.7%**. By default just one AntiNex Core (core) worker manages 100 pre-trained dnn's in memory for making faster predictions and support for manual retraining as needed based off new datasets.

- AntiNex core `accuracy scores`_
- `Jupyter notebook for how it works`_ without any of the AntiNex components as proof of the methodology
- `Jupyter notebook for using a pre-trained dnn to make new predictions with AntiNex`_

AntiNex is a python 3 multi-tenant framework for running a data pipeline for building, training, scoring and refining dnn's. Once trained, dnn's can be loaded into the core for making predictions in near-realtime as the models have already been tuned and pre-trained. The initial focus of AntiNex was to create AI models to defend web applications, but it makes predictions with `classification`_ (used for labeling `attack vs non-attack`_ records) or `regression`_ (like predicting the `closing price of a stock`_) datasets.

.. _accuracy scores: https://github.com/jay-johnson/antinex-core/#antinex-core
.. _Jupyter notebook for how it works: https://github.com/jay-johnson/antinex-core/blob/master/docker/notebooks/AntiNex-Protecting-Django.ipynb
.. _Jupyter notebook for using a pre-trained dnn to make new predictions with AntiNex: https://github.com/jay-johnson/antinex-core/blob/master/docker/notebooks/AntiNex-Using-Pre-Trained-Deep-Neural-Networks-For-Defense.ipynb
.. _classification: https://en.wikipedia.org/wiki/Statistical_classification
.. _regression: https://en.wikipedia.org/wiki/Regression_analysis
.. _attack vs non-attack: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/0d280216e3697f0d2cf7456095e37df64be73040/tests/scaler-full-django-antinex-simple.json#L109-L120
.. _closing price of a stock: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/0d280216e3697f0d2cf7456095e37df64be73040/tests/scaler-regression.json#L5-L11

Quick Start
===========

Clone and Start the Stack
-------------------------

If you have docker-compose you can run the following commands to download all the containers and run the full stack locally (the `ai-core container`_ is ~2.5 GB so it can take a couple minutes to download):

::

    virtualenv -p python3 ~/.venvs/testing
    source ~/.venvs/testing/bin/activate
    pip install antinex-client
    git clone https://github.com/jay-johnson/train-ai-with-django-swagger-jwt /opt/antinex-api
    cd /opt/antinex-api

    # start all the containers from the compose.yml file: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/master/compose.yml
    ./run-all.sh 
    Starting all containers with: compose.yml
    Creating redis    ... done
    Creating jupyter  ... done
    Creating pgadmin  ... done
    Creating postgres ... done
    Creating api      ... done
    Creating core     ... done
    Creating worker   ... done
    Creating pipeline ... done

    # check the containers are running
    docker ps
    CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS              PORTS                    NAMES
    cb0d0e8e582e        jayjohnson/ai-core:latest   "/bin/sh -c 'cd /opt…"   33 seconds ago      Up 32 seconds                                worker
    4b0c44c99472        jayjohnson/ai-core:latest   "/bin/sh -c 'cd /opt…"   33 seconds ago      Up 32 seconds                                pipeline
    bd3c488036dd        jayjohnson/ai-core:latest   "/bin/sh -c 'cd /opt…"   34 seconds ago      Up 33 seconds                                core
    a3093e2632b7        jayjohnson/ai-core:latest   "/bin/sh -c 'cd /opt…"   34 seconds ago      Up 33 seconds                                api
    3839a0af82ec        jayjohnson/pgadmin4:1.0.0   "python ./usr/local/…"   35 seconds ago      Up 33 seconds       0.0.0.0:83->5050/tcp     pgadmin
    b4ea601f28cd        redis:4.0.5-alpine          "docker-entrypoint.s…"   35 seconds ago      Up 33 seconds       0.0.0.0:6379->6379/tcp   redis
    c5eb07041509        postgres:10.2-alpine        "docker-entrypoint.s…"   35 seconds ago      Up 34 seconds       0.0.0.0:5432->5432/tcp   postgres
    9da0440864e0        jayjohnson/ai-core:latest   "/opt/antinex-core/d…"   35 seconds ago      Up 34 seconds                                jupyter

.. _ai-core container: https://hub.docker.com/r/jayjohnson/ai-core/

Migrate the DB
--------------

SSH into the Django container and run the migration:

::

    docker exec -it worker bash
    cd /opt/antinex-api
    ./run-migrations.sh
    exit

Train the Django Neural Network with 99.8% Accuracy
---------------------------------------------------

::

    # train a deep neural network with the included antinex-datasets
    ai_train_dnn.py -u root -p 123321 -f tests/only-publish-scaler-full-django.json

    ...
    ... more logs
    ...

    2018-03-29 20:50:13,306 - ai-client - INFO - started job.id=1 job.status=initial with result.id=1 result.status=initial

    ...
    30199    -1.0 -1.000000  -1.000000  

    [30200 rows x 72 columns]

    # Here's how to watch what the containers are doing:
    # AntiNex Core:
    # docker logs -f core
    # AntiNex REST API:
    # docker logs -f api
    # AntiNex REST API Celery Worker:
    # docker logs -f worker

Get the Accuracy, Training and Prediction Results
-------------------------------------------------

Return the 30,200 predicted records and accuracy scores (which were 99.826%) from in the database.

::

    ai_get_results.py -u root -p 123321 -i 1
    2018-03-29 20:52:26,348 - ai-client - INFO - creating client user=root url=http://localhost:8080 result_id=1
    2018-03-29 20:52:26,349 - ai-client - INFO - loading request in result_id=1
    2018-03-29 20:52:26,360 - ai-client - INFO - log in user=root url=http://localhost:8080/api-token-auth/ ca_file=None cert=None
    2018-03-29 20:52:30,876 - ai-client - INFO - accuracy=99.82615894039735 num_results=30200
    2018-03-29 20:52:30,876 - ai-client - INFO - done getting result.id=1

Make Predictions with Your New Pre-trained Neural Network
---------------------------------------------------------

Note: this is using the same HTTP Request JSON dictionary as the initial training, but this time the AntiNex Core will reuse the pre-trained deep neural network for making new predictions.

::

    ai_train_dnn.py -u root -p 123321 -f tests/only-publish-scaler-full-django.json

    ...

    30199    -1.0 -1.000000  -1.000000  

    [30200 rows x 72 columns]

Get the New Prediction Records and Results
------------------------------------------

::

    ai_get_results.py -u root -p 123321 -i 2

API Examples
============

.. toctree::
   :maxdepth: 2

   api-examples

AntiNex Stack Status
---------------------

The AntiNex REST API is part of the AntiNex stack:

.. list-table::
   :header-rows: 1

   * - Component
     - Build
     - Docs Link
     - Docs Build
   * - `REST API <https://github.com/jay-johnson/train-ai-with-django-swagger-jwt>`__
     - .. image:: https://travis-ci.org/jay-johnson/train-ai-with-django-swagger-jwt.svg?branch=master
           :alt: Travis Tests
           :target: https://travis-ci.org/jay-johnson/train-ai-with-django-swagger-jwt.svg
     - `Docs <http://antinex.readthedocs.io/en/latest/>`__
     - .. image:: https://readthedocs.org/projects/antinex/badge/?version=latest
           :alt: Read the Docs REST API Tests
           :target: https://readthedocs.org/projects/antinex/badge/?version=latest
   * - `Core Worker <https://github.com/jay-johnson/antinex-core>`__
     - .. image:: https://travis-ci.org/jay-johnson/antinex-core.svg?branch=master
           :alt: Travis AntiNex Core Tests
           :target: https://travis-ci.org/jay-johnson/antinex-core.svg
     - `Docs <http://antinex-core-worker.readthedocs.io/en/latest/>`__
     - .. image:: https://readthedocs.org/projects/antinex-core-worker/badge/?version=latest
           :alt: Read the Docs AntiNex Core Tests
           :target: http://antinex-core-worker.readthedocs.io/en/latest/?badge=latest
   * - `Network Pipeline <https://github.com/jay-johnson/network-pipeline>`__
     - .. image:: https://travis-ci.org/jay-johnson/network-pipeline.svg?branch=master
           :alt: Travis AntiNex Network Pipeline Tests
           :target: https://travis-ci.org/jay-johnson/network-pipeline.svg
     - `Docs <http://antinex-network-pipeline.readthedocs.io/en/latest/>`__
     - .. image:: https://readthedocs.org/projects/antinex-network-pipeline/badge/?version=latest
           :alt: Read the Docs AntiNex Network Pipeline Tests
           :target: https://readthedocs.org/projects/antinex-network-pipeline/badge/?version=latest
   * - `AI Utils <https://github.com/jay-johnson/antinex-utils>`__
     - .. image:: https://travis-ci.org/jay-johnson/antinex-utils.svg?branch=master
           :alt: Travis AntiNex AI Utils Tests
           :target: https://travis-ci.org/jay-johnson/antinex-utils.svg
     - `Docs <http://antinex-ai-utilities.readthedocs.io/en/latest/>`__
     - .. image:: https://readthedocs.org/projects/antinex-ai-utilities/badge/?version=latest
           :alt: Read the Docs AntiNex AI Utils Tests
           :target: http://antinex-ai-utilities.readthedocs.io/en/latest/?badge=latest
   * - `Client <https://github.com/jay-johnson/antinex-client>`__
     - .. image:: https://travis-ci.org/jay-johnson/antinex-client.svg?branch=master
           :alt: Travis AntiNex Client Tests
           :target: https://travis-ci.org/jay-johnson/antinex-client.svg
     - `Docs <http://antinex-client.readthedocs.io/en/latest/>`__
     - .. image:: https://readthedocs.org/projects/antinex-client/badge/?version=latest
           :alt: Read the Docs AntiNex Client Tests
           :target: https://readthedocs.org/projects/antinex-client/badge/?version=latest

More Included App URLs
======================

Jupyter Slides on How the Analysis Works
----------------------------------------

.. note:: The **left** and **right** arrow keys navigate the slides in the browser.

http://localhost:8889/Slides-AntiNex-Protecting-Django.slides.html#/

http://localhost:8890/Slides-AntiNex-Using-Pre-Trained-Deep-Neural-Networks-For-Defense.slides.html#/

Django REST API with Swagger
----------------------------

Credentials: **root** and **123321**

http://localhost:8080/swagger/

- `Build and Train a DNN`_
- `Get Training Predictions and Accuracy Results`_
- `Get Training Job Record`_
- `Prepare a New Dataset`_

.. _Build and Train a DNN: http://localhost:8080/swagger/#!/ml/ml_create
.. _Get Training Predictions and Accuracy Results: http://localhost:8080/swagger/#!/mlresults/mlresults_read
.. _Get Training Job Record: http://localhost:8080/swagger/#!/ml/ml_read
.. _Prepare a New Dataset: http://localhost:8080/swagger/#!/mlprepare/mlprepare_create

Django-hosted Sphinx Docs
-------------------------

http://localhost:8080/docs/

Jupyter
-------

Login with: **admin**

http://localhost:8888/

Browse the Postgres DB with pgAdmin4
------------------------------------

Credentials: **admin@email.com** and **postgres**

http://localhost:83

So why does this matter?
========================

- There is no free software we can use today that can share and continually learn how to better defend software applications and our networks against attacks
- AI for network security is a vendor lock-in play, and this approach is already beating the best scores I see online
- Without open datasets and shared best-of-AI-model definitions, our networks will continue to be susceptible to attacks that are easy to defend (antivirus has been doing this same approach for years but it is not good enough)
- Build your own 99.7% accurate dnn within minutes of running the dockerized stack
- Building new training datasets with your own attack and non-attack data takes a matter of minutes
- Replay and prediction history is stored on the user's account within the included postgres database 
- The same core can run on any system that can run python 3 (it can be backported to python 2 for IoT devices as all the internal components like Keras and Tensorflow still run on python 2)

How does it work?
=================

AntiNex is three custom python components that run distributed and are independently scalable. Like many other distributed systems, it utilizes a publisher-subscriber implementation to run a data pipeline with the final step being everything gets recorded in the `postgres database`_ (including all training, predictions and model definitions).

.. _postgres database: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/0d280216e3697f0d2cf7456095e37df64be73040/compose.yml#L5-L15

Here is the workflow for training of a Deep Neural Network with AntiNex. As a user you just have to start the docker stack, and submit a request over HTTP:

.. image:: https://imgur.com/M1vwVoW.png
    :alt: Training a Deep Neural Network with just an HTTP Request

Components
==========

Network Pipeline
----------------

**Traffic Capture Data Pipeline**

Here is how the **capture agents** would be set up for capturing network traffic across many hosts. These agents create a network traffic feed that is aggregated in a common, shared message broker (redis by default). 

.. image:: https://imgur.com/ZVLOYX8.png
    :alt: AntiNex - Distributed Network Pipeline on Monitored Hosts

.. warning:: **Capture agents** are going to sniff your network so be extremely careful where you deploy them. **Capture agents** must be run as **root** to capture traffic from all OSI layers. Also, **capture agents** should not run inside docker containers as docker is very noisy on the network (which I did not know when I started building this). Lastly, none of the docker compose files should be monitoring your network traffic without your explicit knowledge. Please contact me if you find one that does, and I will immediately remove it.

.. note:: The included **pipeline** container is only running the subscriber that saves CSVs and POSTs predictions to the REST API which make it easier to get started. Run this to verify what is running in the container:

    ::

        docker exec -it pipeline ps auwwx
        USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
        runner       1  0.2  0.0   4340   812 ?        Ss   07:32   0:00 /bin/sh -c cd /opt/antinex-pipeline && . ~/.venvs/venvdrfpipeline/bin/activate && /opt/antinex-pipeline/network_pipeline/scripts/packets_redis.py
        runner      10 12.8  0.5 409060 66196 ?        Sl   07:32   0:00 python /opt/antinex-pipeline/network_pipeline/scripts/packets_redis.py
        runner      17  0.0  0.0  19192  2408 pts/0    Rs+  07:32   0:00 ps auwwx


    This subscriber script is on GitHub:

    https://github.com/jay-johnson/network-pipeline/blob/master/network_pipeline/scripts/packets_redis.py

Please refer to the repository for the latest code and documentation: https://github.com/jay-johnson/network-pipeline

This repository allows users to capture network traffic in real-time from many machines running any of the `capture agents`_. These agents become a network traffic feed which is aggregated in a common hub (`redis`_).

These pre-configured capture agents perform the following steps in order:

#.  Record network traffic based off easy-to-write network filters 
#.  Flatten captured traffic packets into dictionaries (using pandas json-normalize)

    #.  Assemble a csv file after capturing a configurable number of packets (100 by default)
    #.  Save the csv data to disk

#.  Post the csv data as JSON to the REST API using the `antinex-client`_

.. toctree::
   :maxdepth: 2
    
   network-pipeline

.. _capture agents: https://github.com/jay-johnson/network-pipeline/tree/1db3d340a1c6cef39d68c9e01e3065b3631e03f2#detailed-version
.. _redis: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/0d280216e3697f0d2cf7456095e37df64be73040/compose.yml#L29-L35
.. _antinex-client: https://github.com/jay-johnson/antinex-client


REST API
--------

**Multi-tenant service with Swagger, Celery and JWT**

Please refer to the repository for the latest code and documentation: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt

The REST API is the gateway for running anything in AntiNex. Only authenticated users can use the included API requests for:

#.  Preparing a New Dataset

    Here is the workflow for Preparing Datasets. CSVs must be synced across the hosts running the REST API and Celery Workers to function.

    .. image:: https://imgur.com/Q4JTMV5.png
       :alt: AntiNex - Prepare a New Dataset

#.  Running a Training Job
#.  Making New Predictions using Pre-trained Deep Neural Networks

    Here is the workflow. Notice CSVs are not required on any of the hosts anymore.

    .. image:: https://imgur.com/PkjCkZk.png
       :alt: AntiNex - Making New Prediction with a Pre-trained Deep Neural Network

#.  Getting a Job's record
#.  Getting a Job's Results including predictions
#.  Managing User accounts

.. toctree::
   :maxdepth: 2
    
   antinex-api

AntiNex Core
------------

**A Celery Worker that can Train and use Pre-trained Models**

Please refer to the repository for the latest code and documentation: https://github.com/jay-johnson/antinex-core

The core is a backend worker that supports two API requests: 

#.  Train a new model
#.  Predict using a pre-trained model (if the model does not exist it will initiate a training job)

By default, the core can support up to 100 pre-trained dnn's for making predictions. Once predictions are finished, the core uses celery to call the REST API's celery worker to record the results in the postgres database. The core is decoupled from a database for keeping it fast and so it can run on constrained environments (IoT).

In the future the core will support loading the weights and model files from disk and out of S3, but that's for a future release.

.. toctree::
   :maxdepth: 2
    
   antinex-core

Additional Components
=====================

AntiNex Client
--------------

Please refer to the repository for the latest code and documentation: https://github.com/jay-johnson/antinex-client

This repository is a python client for interacting with the REST API.

.. toctree::
   :maxdepth: 2
    
   antinex-client

AntiNex Utils
-------------

Please refer to the repository for the latest code and documentation: https://github.com/jay-johnson/antinex-client

This repository is a standalone library that uses Scikit-Learn, Keras and Tensorflow to:

#.  Create dnn's from either: JSON or default values
#.  Transform datasets into scaler normalized values
#.  Make predictions with new or pre-trained dnn's for classification and regression problems
#.  Merge predictions with the original dataset for easier review and analysis

.. toctree::
   :maxdepth: 2
    
   antinex-utils

API Reference
=============

.. toctree::
   :maxdepth: 2

   pipeline
   job_utils
   serializers
   modules/models
   faq.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

What AntiNex is Not
===================

There's a lot of moving pieces in AI, and I wanted to be clear what is currently not supported:

#.  Custom layers or custom Deep Neural Network models - only Keras Sequential neural networks, KerasRegressor, KerasClassifier, Stratified Kfolds, cross validation scoring, Scalers, Add and Dropout are supported. PR's are always welcomed!
#.  Able to tell what your applications are doing today that is good, non-attack traffic out of the box. AntiNex requires recording how the network is being used in normal operation + identifying what you want to protect (do you want tcp traffic only? or a combination of tcp + udp + arp?). It uses the captured traffic to build the initial training dataset.
#.  Exotic attacks - The network pipeline includes the Zed Attack Proxy (ZAP) for OWASP dynamic security analysis. This tool attacks using a fuzzing attack on web applications. ZAP was used to generate the latest attack datasets, and there is no guarantee the latest dnn's will always be effective with attacks I have not seen yet. Please share your findings and reach out if you know how to generate new, better attack simulations to help us all. PR's are always welcomed!
#.  Image predictions and Convoluted Neural Networks - it's only works on numeric datasets.
#.  Recurrent Neural Networks - I plan on adding LTSM support into the antinex-utils, but the scores were already good enough to release this first build.
#.  Embedding Layers - I want to add payload deserialization to the packet processing with support for decrypting traffic, but the dnn scores were good enough to skip this feature for now.
#.  Adversarial Neural Networks - I plan on creating attack neural networks from the datasets to beat up the trained ones, but this is a 2.0 feature at this point.
#.  Saving models to disk is broken - I have commented out the code and found a keras issue that looks like the same problem I am hitting... I hope it's fixed soon so we can share model files via S3.

Disclaimers and Legal
=====================

#.  This is a tool that requires capturing your network traffic to be effective. I am not legally responsible for any damaging or incriminating network traffic you record.
#.  I am not legally responsible for where you deploy this tool. It is meant to help educate how to defend.
#.  This is still an emerging technology, and I am not claiming it will work to defend everything out there on the internet. It works very well for predicting when an attack using OWASP fuzzing attacks are targeting web applications. I am not legally responsible if you run this and you still get hacked, lose data, lose your job, lose your money, destroyed personal property or anything worse. I built it to educate how to build your own deep neural networks to defend. It will forever be an ongoing battle and arms race with malicious actors on the internet trying to beat every claimed-unbeatable fortress.


