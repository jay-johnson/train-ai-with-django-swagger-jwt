Django REST Framework + JWT + Swagger + Keras + Tensorflow
==========================================================

Automate training AI to defend applications with a Django 2.0+ REST Framework application + Swagger and JWT. The Swagger API supports **Prepare Dataset** and **Run Deep Neural Network with new Dataset** requests. These calls are used by the included client scripts in the ``tests`` directory and are ready for automation on networks and infrastructure. For more details please refer to the parent `Network Pipeline`_ repository.

This repository was built to help capture ``non-attack`` network traffic and to improve the accuracy of the Keras + Tensorflow Deep Neural Networks by providing them a simple multi-tenant REST API that has Swagger + JWT authentication baked into a single web application. It also does not require a database (unless you want to set it up), and will be scaled out with `Celery Connectors`_ in the future.

.. _Network Pipeline: https://github.com/jay-johnson/network-pipeline
.. _Celery Connectors: https://github.com/jay-johnson/celery-connectors

I plan to automate the tests in a loop and then release the captured HTTP traffic to compile the first ``non-attack`` dataset for pairing up with the OWASP ``attack`` data which is already recorded and available in:

https://github.com/jay-johnson/network-pipeline-datasets

Watch Getting Started in under a minute
=======================================

.. raw:: html

    <a href="https://asciinema.org/a/Ct8TS1PMPminXBr5xoojTZq89" target="_blank"><img src="https://asciinema.org/a/160914.png"/></a>

Install
=======

This was tested on Ubuntu 17.10.

::

    ./install.sh

Start
=====

::

    ./start.sh
    Starting Django listening on TCP port 8080
    http://localhost:8080/swagger

    django-configurations version 2.0, using configuration 'Development'
    Performing system checks...

    2018-02-03 08:25:41,252 - prepare - INFO - start - prepare
    Using TensorFlow backend.
    System check identified no issues (0 silenced).
    February 03, 2018 - 08:25:42
    Django version 2.0, using settings 'drf_network_pipeline.settings'
    Starting development server at http://0.0.0.0:8080/
    Quit the server with CONTROL-C.


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

Automation
==========

Clone the datasets repository
-----------------------------

git clone https://github.com/jay-johnson/network-pipeline-datasets /opt/datasets

Prepare a new Dataset from Captured Recordings
----------------------------------------------

::

    cd tests
    ./build-new-dataset.py

Train a Keras Deep Neural Network with Tensorflow
-------------------------------------------------

::

    cd tests
    create-keras-dnn.py

    ...

    2018-02-03 00:31:24,342 - create-keras-dnn - INFO - SUCCESS - Post Response status=200 reason=OK
    2018-02-03 00:31:24,342 - create-keras-dnn - INFO - {'job': {'id': 1, 'user_id': 1, 'user_name': 'root', 'title': 'Keras DNN - network-pipeline==1.0.9', 'desc': 'Tensorflow backend with simulated data', 'ds_name': 'cleaned', 'algo_name': 'dnn', 'ml_type': 'keras', 'status': 'initial', 'control_state': 'active', 'predict_feature': 'label_value', 'training_data': {}, 'pre_proc': {}, 'post_proc': {}, 'meta_data': {}, 'tracking_id': 'ml_701552d5-c761-4c69-9258-00d05ff81a48', 'version': 1, 'created': '2018-02-03 08:31:17', 'updated': '2018-02-03 08:31:17', 'deleted': ''}, 'results': {'id': 1, 'user_id': 1, 'user_name': 'root', 'job_id': 1, 'status': 'finished', 'version': 1, 'acc_data': {'accuracy': 83.7837837300859}, 'error_data': None, 'created': '2018-02-03 08:31:24', 'updated': '2018-02-03 08:31:24', 'deleted': ''}}

Development
===========

Swagger Prepare a new Dataset from Captured Recordings
------------------------------------------------------

http://localhost:8080/swagger/?next=/swagger/#!/mlprepare/mlprepare_create

Paste in the following values and click **Try it Out**:

::

    {
        "title": "Prepare new Dataset from recordings",
        "desc": "",
        "ds_name": "new_recording",
        "full_file": "/tmp/fulldata_attack_scans.csv",
        "clean_file": "/tmp/cleaned_attack_scans.csv",
        "meta_prefix": "metadata",
        "output_dir": "/tmp/",
        "ds_dir": "/opt/datasets",
        "ds_glob_path": "/opt/datasets/*/*.csv",
        "pipeline_files": "{\"attack_files\": []}",
        "meta_data": "{}",
        "post_proc": "{ \"drop_columns\" [ \"src_file\", \"raw_id\", \"raw_load\", \"raw_hex_load\", \"raw_hex_field_load\", \"pad_load\", \"eth_dst\", \"eth_src\", \"ip_dst\", \"ip_src\" ], \"predict_feature\" \"label_name\" }",
        "label_rules": "{ \"set_if_above\": 85, \"labels\": [\"not_attack\", \"attack\"], \"label_values\": [0, 1] }",
        "version": 1
    }



Swagger Train a Keras Deep Neural Network with Tensorflow
---------------------------------------------------------

http://localhost:8080/swagger/?next=/swagger/#!/ml/ml_run_create

Paste in the following values and click **Try it Out**:

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

Linting
-------

flake8 .

pycodestyle --exclude=.tox,.eggs

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
