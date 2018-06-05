Fuzzball
--------

A testing framework for service endpoints. Create network traffic for compiling datasets with `AntiNex <https://github.com/jay-johnson/train-ai-with-django-swagger-jwt.git>`__. 

Use Ansible playbooks or a command line tool to run tests over:

- SSH
- Telnet
- Coming soon - Swagger REST APIs with JWT

This is a research project.

AntiNex Stack Status
--------------------

This project is a testing tool used by AntiNex. Here is documentation to the rest of the components.

.. list-table::
   :header-rows: 1

   * - Component
     - Build
     - Docs Link
     - Docs Build
   * - `Fuzzball <https://github.com/jay-johnson/fuzzball>`__
     - .. image:: https://travis-ci.org/jay-johnson/fuzzball.svg?branch=master
           :alt: Travis Fuzzball Tests
           :target: https://travis-ci.org/jay-johnson/fuzzball.svg
     - `Docs <http://fuzzball.readthedocs.io/en/latest/>`__
     - .. image:: https://readthedocs.org/projects/fuzzball/badge/?version=latest
           :alt: Read the Docs Fuzzball Testing Tool
           :target: https://readthedocs.org/projects/fuzzball/badge/?version=latest
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
   * - `Fuzzball <https://github.com/jay-johnson/fuzzball>`__
     - .. image:: https://travis-ci.org/jay-johnson/fuzzball.svg?branch=master
           :alt: Travis Fuzzball Tests
           :target: https://travis-ci.org/jay-johnson/fuzzball.svg
     - `Docs <http://fuzzball.readthedocs.io/en/latest/>`__
     - .. image:: https://readthedocs.org/projects/fuzzball/badge/?version=latest
           :alt: Read the Docs Fuzzball Testing Tool
           :target: https://readthedocs.org/projects/fuzzball/badge/?version=latest

Getting Started
===============

Clone to ``/opt/antinex/fuzzball``:

::

    mkdir -p -m 777 /opt/antinex
    git clone https://github.com/jay-johnson/fuzzball.git /opt/antinex/fuzzball

If you want to use the Ansible playbooks, please set up a python 3 virtualenv:

::

    virtualenv -p python3 /opt/venv && source /opt/venv/bin/activate && pip install -e .

Install SSH Testing Key
=======================

If you want to run ssh tests, make sure the SSH keys are copied over.

::

    ssh-copy-id -i ./tests/keys/defend-key admin@defend1
    /usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "./tests/keys/defend-key.pub"
    The authenticity of host 'defend1 (192.168.0.12)' can't be established.
    Are you sure you want to continue connecting (yes/no)? yes
    /usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
    /usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
    admin@defend1's password:

    Number of key(s) added: 1

    Now try logging into the machine, with:   "ssh 'admin@defend1'"
    and check to make sure that only the key(s) you wanted were added.

Confirm SSH Key Works
=====================

::

    ssh -i ./tests/keys/defend-key admin@defend1
    Last login: Thu Apr 26 16:55:40 2018 from defend1
    To run a command as administrator (user "root"), use "sudo <command>".
    See "man sudo_root" for details.

    admin@defend1:~$ exit
    logout
    Shared connection to defend1 closed.

Ansible Playbooks
-----------------

Fuzzball supports a few operational modes to make automation and integration easier.

The Ansible playbooks are the fastest way to get started. This repository ships with playbooks in the ``ansible`` directory. These playbooks were designed to make it easy to integrate ci/cd tools like Jenkins to start automating fuzzing tests on git webhook events. The following commands were from inside the ``/opt/antinex/fuzzball/ansible`` directory.

Ansible Start Worker
====================

You can start Celery worker pools with this Ansible playbook (you can run it multiple times to start up additional Fuzzball workers too):

::

    ansible-playbook -i inventory-dev worker-start.yml -vvvv
    
If you want to watch the workers' logs you can tail them with:

::

    tail -f /var/log/antinex/fuzzball/fuzz.log

If you want to view the worker processes:

::

    ps auwwx | grep celery | grep fuzzball

Ansible Start SSH Fuzz Jobs
===========================

If you do not have any Celery workers running you can use this command to run all the jobs within 1 process:

::

    ansible-playbook -i inventory-dev fuzz-endpoint.yml -e job_type=ssh -e target=defend1:22 -vvvv

If there are connected Celery workers you can the command below to publish jobs to the workers. Please remember the task will just publish the jobs while the workers will log the progress to the log file: ``/var/log/antinex/fuzzball/fuzz.log``.

::

    ansible-playbook -i inventory-dev celery-fuzz-endpoint.yml -e job_type=ssh -e target=defend1:22 -vvvv

Ansible Start Telnet Fuzz Jobs
==============================

If you do not have any Celery workers running you can use this command to run all the jobs within 1 process:

::

    ansible-playbook -i inventory-dev fuzz-endpoint.yml -e job_type=telnet -e target=defend1:23 -vvvv

If there are connected Celery workers you can the command below to publish jobs to the workers. Please remember the task will just publish the jobs while the workers will log the progress to the log file: ``/var/log/antinex/fuzzball/fuzz.log``.

::

    ansible-playbook -i inventory-dev celery-fuzz-endpoint.yml -e job_type=telnet -e target=defend1:23 -vvvv

Ansible Stop Worker
===================

This will shutdown all the Celery Fuzzball worker processes

::

    ansible-playbook -i inventory-dev worker-stop.yml -vvvv

Docker
------

Fuzzball runs python 3 inside a `docker container image <https://hub.docker.com/r/jayjohnson/antinex-fuzzball>`__ or from python runtime environment like virtualenv or pipenv.

Command Line
------------

The Ansible playbooks set sane defaults for most of the included command line tool's options and arguments. The Ansible playbooks use the latest ``run_fuzzer.py`` usages, if you want to customize it for your own integrations.

::

    run_fuzzer.py -h
    usage: run_fuzzer.py [-h] [-T] [-C CELERY_CONFIG] [-u USERS] [-p PASSWORDS]
                     [-f PROMPT_USERS] [-m PROMPT_PASSWORDS] [-c COMMANDS]
                     [-a ADDRESS_HOST] [-t TARGETS] [-k PRIVATE_KEYS]
                     [-j JOB_TYPE] [-n NAMED_LOGINS] [-N]

    Run fuzzer

    optional arguments:
    -h, --help           show this help message and exit
    -T                   Do not publish jobs to a Fuzz Worker. Run everything in
                        a single process which is useful for testing.
    -C CELERY_CONFIG     Publish jobs to a Fuzz Worker with this celery config
                        file
    -u USERS             users path to users.json file
    -p PASSWORDS         passwords path to passwords.json file
    -f PROMPT_USERS      prompt_users path to passwords.json file
    -m PROMPT_PASSWORDS  prompt_passwords path to prompt_passwords.json file
    -c COMMANDS          commands path to commands.json file
    -a ADDRESS_HOST      single address to use <host:port>
    -t TARGETS           targets path to targets.json file
    -k PRIVATE_KEYS      private_keys path to private_keys.json file
    -j JOB_TYPE          job_type string <telnet|ssh>
    -n NAMED_LOGINS      named_logins path to named_logins.json file
    -N                   (flag) only target the -a <single host to use>

Testing
-------

#.  Run all

    ::

        python setup.py test

#.  Run a test

    ::

        python -m unittest tests.test_telnet.TestFuzzyTelnet.test_start_auth

#.  Run tests until the first failure

    ::

        py.test --maxfail=1 --capture=no tests

Disclaimer
----------

This repository was built for research and education purposes. I am not legally responsible for where you run, use or operate the tools contained in this repository. Please be careful where you use this project and operate it at your own risk to your own software, data and systems.

Linting
-------

::

    flake8 .
    pycodestyle .

License
-------

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/jay-johnson/fuzzball/blob/master/LICENSE

