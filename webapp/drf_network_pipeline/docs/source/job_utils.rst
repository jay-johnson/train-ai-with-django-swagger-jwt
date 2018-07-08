Source Code - Job Helpers
=========================

These are the helper methods for abstracting celery calls from the Django REST Framework Serializers. These are optional for most users, I just find them helpful because the serializers all examine a common dictionary structure instead of custom ones all over the code. The response structure is:

::

    task_response_node = {
        "status": status,
        "err": err,
        "task_name": task_name,
        "data": data,      
        "celery_enabled": celery_enabled,
        "use_cache": use_cache,
        "cache_key": cache_key
    }    

#.  **status** will be a const value from the **drf_network_pipeline.pipeline.consts**

    **Response Status Codes**

    ::

        SUCCESS = 0
        FAILED = 1
        ERR = 2
        EX = 3
        NOTRUN = 4
        INVALID = 5
        NOTDONE = 6

#.  **err** will be an empty string on **SUCCESS** and not-empty if there was a problem
#.  **data** is the result from the Celery worker (if it was used instead of **python manage.py runserver 0.0.0.0:8010**)
#.  **use_cache** is a flag meaning the results ere also cached in the **cache_key** for **django-cacheops** to use (this is not supported yet)
#.  **task_name** is a human readable task label for debugging in the logs

Build Task Request
------------------

.. automodule:: drf_network_pipeline.job_utils.build_task_request
   :members:

Build Task Response
-------------------

.. automodule:: drf_network_pipeline.job_utils.build_task_response
   :members:

Handle Task Method
------------------

.. automodule:: drf_network_pipeline.job_utils.handle_task_method
   :members:

Run Task
--------

.. automodule:: drf_network_pipeline.job_utils.run_task
   :members:

