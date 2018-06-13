AntiNex Core
============

Automating network exploit detection using highly accurate pre-trained deep neural networks.

As of 2018-03-12, the core can repeatedly predict attacks on Django, Flask, React + Redux, Vue, and Spring application servers by training using the pre-recorded `AntiNex datasets`_ with cross validation scores above **~99.8%** with automated scaler normalization.

.. image:: https://travis-ci.org/jay-johnson/antinex-core.svg?branch=master
    :target: https://travis-ci.org/jay-johnson/antinex-core

Accuracy + Training + Cross Validation in a Jupyter Notebook
------------------------------------------------------------

https://github.com/jay-johnson/antinex-core/blob/master/docker/notebooks/AntiNex-Protecting-Django.ipynb

Using a Pre-Trained Deep Neural Network in a Jupyter Notebook
-------------------------------------------------------------

https://github.com/jay-johnson/antinex-core/blob/master/docker/notebooks/AntiNex-Using-Pre-Trained-Deep-Neural-Networks-For-Defense.ipynb

.. _AntiNex datasets: https://github.com/jay-johnson/antinex-datasets

Overview
--------

The core is a Celery worker pool for processing training and prediction requests for deep neural networks to detect network exploits (Nex) using Keras and Tensorflow in near real-time. Internally each worker manages a buffer of pre-trained models identified by the ``label`` from the initial training request. Once trained, a model can be used for rapid prediction testing provided the same ``label`` name is used on the prediction request. Models can also be re-trained by using the training api with the same ``label``. While the initial focus is on network exploits, the repository also includes mock stock data for demonstrating running a worker pool to quickly predict regression data (like stock prices) with many, pre-trained deep neural networks.

This repository is a standalone training and prediction worker pool that is decoupled from the AntiNex REST API:

https://github.com/jay-johnson/train-ai-with-django-swagger-jwt

AntiNex Stack Status
--------------------

AntiNex Core Worker is part of the AntiNex stack:

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

Install
-------

pip install antinex-core

Optional for Generating Images
------------------------------

If you want to generate images please install ``python3-tk`` on Ubuntu.

::

    sudo apt-get install python3-tk

Docker
------

Start the container for browsing with Jupyter:

::

    # if you do not have docker compose installed, you can try installing it with:
    # pip install docker-compose
    cd docker
    ./start-stack.sh

Open Jupyter Notebook with Django Deep Neural Network Analysis
--------------------------------------------------------------

Default password is: ``admin``

http://localhost:8888/notebooks/AntiNex-Protecting-Django.ipynb

View Notebook Presentation Slides
---------------------------------

#.  Use ``Alt + r`` inside the notebook

#.  Use the non-vertical scolling url: http://localhost:8889/Slides-AntiNex-Protecting-Django.slides.html

#.  Use the non-vertical scolling url: http://localhost:8890/Slides-AntiNex-Using-Pre-Trained-Deep-Neural-Networks-For-Defense.slides.html

Run
---

Please make sure redis is running and accessible before starting the core:

::

    redis-cli 
    127.0.0.1:6379>

With redis running and the antinex-core pip installed in the python 3 runtime, use this command to start the core:

::

    ./run-antinex-core.sh

Or with celery:

::

    celery worker -A antinex_core.antinex_worker -l DEBUG

Publish a Predict Request
-------------------------

To train and predict with the new automated scaler-normalized dataset with a 99.8% prediction accuracy for detecting attacks using a wide, two-layer deep neural network with the `AntiNex datasets`_ run the following steps.

.. _AntiNex datasets: https://github.com/jay-johnson/antinex-datasets

Clone
-----

Please make sure to clone the dataset repo to the pre-configured location:

::

    mkdir -p -m 777 /opt/antinex
    git clone https://github.com/jay-johnson/antinex-datasets.git /opt/antinex/antinex-datasets

Django - Train and Predict
--------------------------

::

    ./antinex_core/scripts/publish_predict_request.py -f training/scaler-full-django-antinex-simple.json

Flask - Train and Predict
-------------------------

::

    ./antinex_core/scripts/publish_predict_request.py -f training/scaler-full-flask-antinex-simple.json

React and Redux - Train and Predict
-----------------------------------

::

    ./antinex_core/scripts/publish_predict_request.py -f training/scaler-full-react-redux-antinex-simple.json

Vue - Train and Predict
-----------------------

::

    ./antinex_core/scripts/publish_predict_request.py -f training/scaler-full-vue-antinex-simple.json

Spring - Train and Predict
--------------------------

::

    ./antinex_core/scripts/publish_predict_request.py -f training/scaler-full-spring-antinex-simple.json

Accuracy and Prediction Report
------------------------------

After a few minutes the final report will be printed out like:

::

    2018-03-11 23:35:00,944 - antinex-prc - INFO - sample=30178 - label_value=1.0 predicted=1 label=attack
    2018-03-11 23:35:00,944 - antinex-prc - INFO - sample=30179 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,944 - antinex-prc - INFO - sample=30180 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,944 - antinex-prc - INFO - sample=30181 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,944 - antinex-prc - INFO - sample=30182 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30183 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30184 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30185 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30186 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30187 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30188 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30189 - label_value=1.0 predicted=1 label=attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30190 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,945 - antinex-prc - INFO - sample=30191 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,946 - antinex-prc - INFO - sample=30192 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,946 - antinex-prc - INFO - sample=30193 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,946 - antinex-prc - INFO - sample=30194 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,946 - antinex-prc - INFO - sample=30195 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,946 - antinex-prc - INFO - sample=30196 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,946 - antinex-prc - INFO - sample=30197 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,946 - antinex-prc - INFO - sample=30198 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,946 - antinex-prc - INFO - sample=30199 - label_value=-1.0 predicted=-1 label=not_attack
    2018-03-11 23:35:00,947 - antinex-prc - INFO - Full-Django-AntiNex-Simple-Scaler-DNN made predictions=30200 found=30200 accuracy=99.84685430463577
    2018-03-11 23:35:00,947 - antinex-prc - INFO - Full-Django-AntiNex-Simple-Scaler-DNN - saving model=full-django-antinex-simple-scaler-dnn


If you do not have the datasets cloned locally, you can use the included minimized dataset from the repo:

::

    ./antinex_core/scripts/publish_predict_request.py -f training/scaler-django-antinex-simple.json

Publish a Train Request
-----------------------

::

    ./antinex_core/scripts/publish_train_request.py

Publish a Regression Prediction Request
---------------------------------------

::

    ./antinex_core/scripts/publish_regression_predict.py

JSON API
--------

The AntiNex core manages a pool of workers that are subscribed to process tasks found in two queues (``webapp.train.requests`` and ``webapp.predict.requests``). Tasks are defined as JSON dictionaries and must have the following structure:

::

    {
        "label": "Django-AntiNex-Simple-Scaler-DNN",
        "dataset": "./tests/datasets/classification/cleaned_attack_scans.csv",
        "apply_scaler": true,
        "ml_type": "classification",
        "predict_feature": "label_value",
        "features_to_process": [
            "eth_type",
            "idx",
            "ip_ihl",
            "ip_len",
            "ip_tos",
            "ip_version",
            "tcp_dport",
            "tcp_fields_options.MSS",
            "tcp_fields_options.Timestamp",
            "tcp_fields_options.WScale",
            "tcp_seq",
            "tcp_sport"
        ],
        "ignore_features": [
        ],
        "sort_values": [
        ],
        "seed": 42,
        "test_size": 0.2,
        "batch_size": 32,
        "epochs": 10,
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
                    "num_neurons": 250,
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

Regression prediction tasks are also supported, and here is an example from an included dataset with mock stock prices:

::

    {
        "label": "Scaler-Close-Regression",
        "dataset": "./tests/datasets/regression/stock.csv",
        "apply_scaler": true,
        "ml_type": "regression",
        "predict_feature": "close",
        "features_to_process": [
            "high",
            "low",
            "open",
            "volume"
        ],
        "ignore_features": [
        ],
        "sort_values": [
        ],
        "seed": 7,
        "test_size": 0.2,
        "batch_size": 32,
        "epochs": 50,
        "num_splits": 2,
        "loss": "mse",
        "optimizer": "adam",
        "metrics": [
            "accuracy"
        ],
        "model_desc": {
            "layers": [
                {
                    "activation": "relu",
                    "init": "uniform",
                    "num_neurons": 200
                },
                {
                    "activation": null,
                    "init": "uniform",
                    "num_neurons": 1
                }
            ]
        }
    }

Development
-----------
::

    virtualenv -p python3 ~/.venvs/antinexcore && source ~/.venvs/antinexcore/bin/activate && pip install -e .

Testing
-------

Run all

::

    python setup.py test

Run a test case

::

    python -m unittest tests.test_train.TestTrain.test_train_antinex_simple_success_retrain

Linting
-------

flake8 .

pycodestyle .

License
-------

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/jay-johnson/antinex-core/blob/master/LICENSE

