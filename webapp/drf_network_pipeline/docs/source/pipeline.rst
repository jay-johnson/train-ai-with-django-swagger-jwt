ML Pipeline
===========

These are the methods for developing with the current ML Pipeline app within the Django Rest Framework.

Constants
---------

Constants for the ML 

.. automodule:: drf_network_pipeline.pipeline.consts
   :members:

Building a Response Dictionary
------------------------------

This builds a dictionary that is published to the AntiNex Core within the MLJob's prediction manifest. This dictionary contains how to send the results back to the core. This would allow for an environment to run many Rest APIs and reuse the same core workers.

.. automodule:: drf_network_pipeline.pipeline.build_worker_result_node
   :members:

Creating ML Job Stub Records for Tracking Purposes
--------------------------------------------------

Creates initial ``MLJob`` and ``MLJobResult`` record stub in the database

.. automodule:: drf_network_pipeline.pipeline.create_ml_job_record
   :members:

Creating New Training Datasets
------------------------------

Creates an initial ``MLPrepare`` record stub in the database

.. automodule:: drf_network_pipeline.pipeline.create_ml_prepare_record
   :members:

Celery Tasks
------------

Celery tasks that are handled within the Django Rest API Worker when the environment variable ``CELERY_ENABLED`` is set to ``1``

.. autotask:: drf_network_pipeline.pipeline.tasks.task_ml_job
.. autotask:: drf_network_pipeline.pipeline.tasks.task_ml_prepare
.. autotask:: drf_network_pipeline.pipeline.tasks.task_ml_process_results
.. autotask:: drf_network_pipeline.pipeline.tasks.task_publish_to_core

Utility Methods
---------------

Utility methods

.. automodule:: drf_network_pipeline.pipeline.utils
   :members:
