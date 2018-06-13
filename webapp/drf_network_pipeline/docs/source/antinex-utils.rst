AntiNex AI Utilities
====================

Standalone utilities for training AI.

.. image:: https://travis-ci.org/jay-johnson/antinex-utils.svg?branch=master
    :alt: Travis AntiNex AI Utilities Tests
    :target: https://travis-ci.org/jay-johnson/antinex-utils

.. image:: https://readthedocs.org/projects/antinex-ai-utilities/badge/?version=latest
    :alt: Read the Docs AntiNex AI Utilities Tests
    :target: http://antinex-ai-utilities.readthedocs.io/en/latest/?badge=latest

Used in:

https://github.com/jay-johnson/train-ai-with-django-swagger-jwt

Install
-------

pip install antinex-utils

Development
-----------

#.  Set up the repository

    ::

        mkdir -p -m 777 /opt/antinex
        git clone https://github.com/jay-johnson/antinex-utils.git /opt/antinex/utils
        cd /opt/antinex/utils

#.  Set up the virtual env and install

    ::

        virtualenv -p python3 ~/.venvs/antinexutils && source ~/.venvs/antinexutils/bin/activate && pip install -e .

Testing
-------

Run all

::

    python setup.py test

Run a test case

::

    python -m unittest tests.test_classification.TestClassification.test_classification_deep_dnn

::

    python -m unittest tests.test_regression.TestRegression.test_dataset_regression_using_scaler

AntiNex Stack Status
--------------------

AntiNex AI Utilities is part of the AntiNex stack:

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

Linting
-------

flake8 .

pycodestyle --exclude=.tox,.eggs

License
-------

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/jay-johnson/antinex-utils/blob/master/LICENSE
