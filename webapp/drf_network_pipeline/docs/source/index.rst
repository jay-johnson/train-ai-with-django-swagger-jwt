.. AntiNex - Deep Neural Networks for Defense documentation master file, created by
   sphinx-quickstart on Wed Mar 28 12:37:48 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to AntiNex
==================

Helping build, train and use pre-trained Deep Neural Networks for Defense
-------------------------------------------------------------------------

.. image:: https://imgur.com/pEEnUZT.png
    :alt: AntiNex - Helping build, train and use pre-trained Deep Neural Networks for Defense

What is this?
=============

AntiNex is a free tool for helping anyone defend against software attacks like `internet chemotherapy`_. It does this by helping users craft specialized datasets from network traffic packets in the OSI layers 2, 3, 4 and 5. Once datasets are labeled as attack and non-attack records, you can train your own Deep Neural Networks (dnn's) for identifying attack records across the network. With this approach AntiNex can predict attacks on web applications like: Django, Flask, React and Redux, Vue, and Spring with repeatable accuracies above **99.8%**. By default just one AntiNex Core (core) worker manages 100 pre-trained dnn's in memory for making faster predictions and allowing controled re-training as needed based off new datasets.

- AntiNex core `accuracy scores`_
- `Jupyter notebook`_ showing how it works without any of the AntiNex components as proof of the methodology

AntiNex is a python 3 multi-tenant framework for running a data pipeline for building, training, scoring and refining dnn's. Once trained, dnn's can be loaded into the core for making predictions in near-realtime as the models have already been tuned and pre-trained. The initial focus of AntiNex was to create AI models to defend web applications, but it makes predictions with `classification`_ (used for labeling `attack vs non-attack`_ records) or `regression`_ (like predicting the `closing price of a stock`_) datasets.

.. _internet chemotherapy: https://0x00sec.org/t/internet-chemotherapy/4664
.. _accuracy scores: https://github.com/jay-johnson/antinex-core/#antinex-core
.. _Jupyter notebook: https://github.com/jay-johnson/antinex-core/blob/master/docker/notebooks/AntiNex-Protecting-Django.ipynb
.. _classification: https://en.wikipedia.org/wiki/Statistical_classification
.. _regression: https://en.wikipedia.org/wiki/Regression_analysis
.. _attack vs non-attack: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/0d280216e3697f0d2cf7456095e37df64be73040/tests/scaler-full-django-antinex-simple.json#L109-L120
.. _closing price of a stock: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/0d280216e3697f0d2cf7456095e37df64be73040/tests/scaler-regression.json#L5-L11

Why do I care?
==============

- There is no free software we can use today that can share and continually learn how to better defend software applications and our networks against attacks
- AI for network security is a vendor lock-in play, and this approach is already beating the best scores I see online
- Without open datasets and shared best-of-AI-model definitions, our networks will continue to be suseptible to attacks that are easy to defend (antivirus has been doing this same approach for years but it is not good enough)
- Build your own 99.8% accurate dnn within minutes of running the dockerized stack
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

Network Pipeline - Traffic Capture Data Pipeline 
------------------------------------------------

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
   :caption: Contents:
    
   network-pipeline

.. _capture agents: https://github.com/jay-johnson/network-pipeline/tree/1db3d340a1c6cef39d68c9e01e3065b3631e03f2#detailed-version
.. _redis: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/0d280216e3697f0d2cf7456095e37df64be73040/compose.yml#L29-L35
.. _antinex-client: https://github.com/jay-johnson/antinex-client


REST API - Multi-tenant service with Swagger, Celery and JWT
------------------------------------------------------------

Please refer to the repository for the latest code and documentation: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt

The REST API is the gateway for running anything in AntiNex. Only authenticated users can use the included API requests for:

#.  Preparing a Dataset
#.  Running a Train or Predict Job
#.  Getting a Job's record
#.  Getting a Job's Results including predictions
#.  Managing User accounts

.. toctree::
   :maxdepth: 2
   :caption: Contents:
    
   antinex-api

AntiNex Core - Celery Worker that can Train and use Pre-trained Models
----------------------------------------------------------------------

Please refer to the repository for the latest code and documentation: https://github.com/jay-johnson/antinex-core

The core is a backend worker that supports two API requests: 

#.  Train a new model
#.  Predict using a pre-trained model (if the model does not exist it will initiate a training job)

By default, the core can support up to 100 pre-trained dnn's for making predictions. Once predictions are finished, the core uses celery to call the REST API's celery worker to record the results in the postgres database. The core is decoupled from a database for keeping it fast and so it can run on constrained environments (IoT).

In the future the core will support loading the weights and model files from disk and out of S3, but that's for a future release.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
    
   antinex-core

Additional Components
=====================

AntiNex Client
--------------

Please refer to the repository for the latest code and documentation: https://github.com/jay-johnson/antinex-client

This repository is a python client for interacting with the REST API.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
    
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
   :caption: Contents:
    
   antinex-utils

What AntiNex is Not and Disclaimers
===================================

There's a lot of moving pieces in AI, and I wanted to be clear what is currently not supported:

#.  Custom layers or custom Deep Neural Network models - only Keras Sequential neural networks, KerasRegressor, KerasClassifier, Stratified Kfolds, cross validation scoring, Scalers, Add and Dropout are supported. PR's are always welcomed!
#.  Able to tell what your applications are doing today that is good, non-attack traffic out of the box. AntiNex requires recording how the network is being used in normal operation + identifying what you want to protect (do you want tcp traffic only? or a combination of tcp + udp + arp?). It uses the captured traffic to build the intial training dataset.
#.  Exotic attacks - The network pipeline includes the Zed Attack Proxy (ZED) for OWASP dynamic security analysis. This tool attacks using a fuzzing attack on web applications. ZED was used to generate the latest attack datasets, and there is no guarantee the latest dnn's will always be effective with attacks I have not seen yet. Please share your findings and reach out if you know how to generate new, better attack simulations to help us all. PR's are always welcomed!
#.  Image predictions and Convoluted Neural Networks - it's only works on numeric datasets.
#.  Recurrent Neural Networks - I plan on adding LTSM support into the antinex-utils, but the scores were already good enough to release this first build.
#.  Embedding Layers - I want to add payload deserialization to the packet processing with support for decrypting traffic, but the dnn scores were good enough to skip this feature for now.
#.  Adversarial Neural Networks - I plan on creating attack neural networks from the datasets to beat up the trained ones, but this is a 2.0 feature at this point.
#.  Saving models to disk is broken - I have commented out the code and found a keras issue that looks like the same problem I am hitting... I hope it is resovled so we can share model files via S3.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
    
   modules/models
   faq.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
