AntiNex Python Client
=====================

Python API Client for training deep neural networks with the REST API running

https://github.com/jay-johnson/train-ai-with-django-swagger-jwt

.. image:: https://travis-ci.org/jay-johnson/antinex-client.svg?branch=master
    :target: https://travis-ci.org/jay-johnson/antinex-client

.. image:: https://readthedocs.org/projects/antinex-client/badge/?version=latest
    :target: http://antinex-client.readthedocs.io/en/latest/?badge=latest

Install
-------

pip install antinex-client

AntiNex Stack Status
--------------------

AntiNex client is part of the AntiNex stack:

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

Run Predictions
===============

These examples use the default user ``root`` with password ``123321``. It is advised to change this to your own user in the future.

Train a Deep Neural Network with a JSON List of Records
-------------------------------------------------------

::

    ai -u root -p 123321 -f examples/predict-rows-scaler-django-simple.json

Train a Deep Neural Network to Predict Attacks with the AntiNex Datasets
------------------------------------------------------------------------

Please make sure the datasets are available to the REST API, Celery worker, and AntiNex Core worker. The datasets are already included in the docker container ``ai-core`` provided in the default ``compose.yml`` file:

https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/51f731860daf134ea2bd3b68468927c614c83ee5/compose.yml#L53-L104

If you're running outside docker make sure to clone the repo with:

::

    git clone https://github.com/jay-johnson/antinex-datasets.git /opt/antinex/antinex-datasets    

Train the Django Defensive Deep Neural Network
----------------------------------------------

Please wait as this will take a few minutes to return and convert the predictions to a pandas DataFrame.

::

    ai -u root -p 123321 -f examples/scaler-full-django-antinex-simple.json 

    ...

    [30200 rows x 72 columns]

Using Pre-trained Neural Networks to make Predictions
-----------------------------------------------------

The `AntiNex Core`_ manages pre-trained deep neural networks in memory. These can be used with the REST API by adding the ``"publish_to_core": true`` to a request while running with the `REST API compose.yml`_ docker containers running.

Run:

::

    ai -u root -p 123321 -f examples/publish-to-core-scaler-full-django.json

Here is the diff between requests that will run using a pre-trained model and one that will train a new neural network:

::

    antinex-client$ diff examples/publish-to-core-scaler-full-django.json examples/scaler-full-django-antinex-simple.json 
    5d4
    <     "publish_to_core": true,
    antinex-client$

.. _AntiNex Core: https://github.com/jay-johnson/antinex-core
.. _REST API compose.yml: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/master/compose.yml

Prepare a Dataset
-----------------

::

    ai_prepare_dataset.py -u root -p 123321 -f examples/prepare-new-dataset.json

Get Job Record for a Deep Neural Network
----------------------------------------

Get a user's MLJob record by setting: ``-i <MLJob.id>``

This include the model json or model description for the Keras DNN.

::

    ai_get_job.py -u root -p 123321 -i 4

Get Predictions Results for a Deep Neural Network
-------------------------------------------------

Get a user's MLJobResult record by setting: ``-i <MLJobResult.id>``

This includes predictions from the training or prediction job.

::

    ai_get_results.py -u root -p 123321 -i 4

Get a Prepared Dataset
----------------------

Get a user's MLPrepare record by setting: ``-i <MLPrepare.id>``

::

    ai_get_prepared_dataset.py -u root -p 123321 -i 15

Using a Client Built from Environment Variables
-----------------------------------------------

This is how the `Network Pipeline`_ streams data to the `AntiNex Core`_ to make predictions with pre-trained models.

Export the example environment file:

::

    source examples/example-prediction.env

Run the client prediction stream script

::

    ai_env_predict.py -f examples/predict-rows-scaler-full-django.json

.. _Network Pipeline: https://github.com/jay-johnson/network-pipeline
.. _AntiNex Core: https://github.com/jay-johnson/antinex-core

Development
-----------
::

    virtualenv -p python3 ~/.venvs/antinexclient && source ~/.venvs/antinexclient/bin/activate && pip install -e .

Testing
-------

Run all

::

    python setup.py test

Linting
-------

flake8 .

pycodestyle .

License
-------

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/jay-johnson/antinex-client/blob/master/LICENSE
