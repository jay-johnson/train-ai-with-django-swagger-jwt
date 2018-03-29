AntiNex Utilities
=================

Standalone utilities for training AI.

Used in:

https://github.com/jay-johnson/train-ai-with-django-swagger-jwt

Install
-------

pip install antinex-utils

Development
-----------
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

Linting
-------

flake8 .

pycodestyle --exclude=.tox,.eggs

License
-------

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/jay-johnson/antinex-utils/blob/master/LICENSE
