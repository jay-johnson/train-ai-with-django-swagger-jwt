AntiNex API Examples
====================

Using Curl Commands with the REST API

Login a User
------------

This will get the JWT token for a user. In this example it is the only user on an initial system **root**:

::

    curl -s -X POST \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        -d '{ "username": "root", "password": "123321" }' \
        'http://0.0.0.0:8080/api-token-auth/'

    {"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6InJvb3QiLCJleHAiOjE1MjI0MjM0NzEsImVtYWlsIjoicm9vdEBlbWFpbC5jb20ifQ.LBfDvnoG5ilLWgB7lg6EWuR4QkspppF9NHy7oyCmh1s"}

If you want to store the token in a simple variable like **token** use:

::

    token=$(curl -s -X POST \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        -d '{ "username": "root", "password": "123321" }' \
        'http://0.0.0.0:8080/api-token-auth/' \
        | sed -e 's/"/ /g' | awk '{print $4}')
    echo $token
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6InJvb3QiLCJleHAiOjE1MjI0MjM2MDQsImVtYWlsIjoicm9vdEBlbWFpbC5jb20ifQ.SdQBLTFvA4qQqKsCyU4Quu2b5VLDjt3QO1b29njfl48

Prepare a Dataset
=================

To use these examples please clone the `Network Pipeline Datasets repository`_ locally:

::

    git clone https://github.com/jay-johnson/network-pipeline-datasets /opt/datasets

You can also use the `AntiNex Datasets repository`_ if you want, they assume you want to build a dataset with the included OWASP fuzzing attack data captured during a ZAP attack simulation in with your own captured CSV files.

.. _Network Pipeline Datasets repository: https://github.com/jay-johnson/network-pipeline-datasets
.. _AntiNex Datasets repository: https://github.com/jay-johnson/antinex-datasets

.. toctree::
   :maxdepth: 2
       
   prepare-antinex-dataset-django.rst
   prepare-antinex-dataset-flask-restplus.rst
   prepare-antinex-dataset-react-redux.rst
   prepare-antinex-dataset-spring.rst
   prepare-antinex-dataset-vue.rst

Here is the full HTTP request for preparing a dataset. For reference:

Inputs
------

**ds_glob_path** is where the CSV files are on disk.

Outputs
-------

**clean_file** will be the training-ready CSV file create
**full_file** is a full CSV file from the prepared datasets, this means it will have things like dates, strings and other non-numeric values that make it not training-ready without additional clean up steps. Please use the CSV file created in the **clean_file** value for training a Deep Neural Network.

will be an output the from the ``packet-redis.py`` script running in the **pipeline** container. The script writes csv files

::

    {
        "title": "Prepare new Dataset from recordings",
        "desc": "",
        "ds_name": "new_recording",
        "ds_glob_path": "/opt/datasets/*/*.csv",
        "ds_dir": "/opt/datasets",
        "full_file": "/tmp/fulldata_attack_scans.csv",
        "clean_file": "/tmp/cleaned_attack_scans.csv",
        "meta_suffix": "metadata.json",
        "output_dir": "/tmp/",
        "pipeline_files": {
            "attack_files": []
        },
        "meta_data": {},
        "post_proc": {
            "drop_columns": [
                "src_file",
                "raw_id",
                "raw_load",
                "raw_hex_load",
                "raw_hex_field_load",
                "pad_load",
                "eth_dst",
                "eth_src",
                "ip_dst",
                "ip_src"
            ],
            "predict_feature": "label_name"
        },
        "label_rules": {
            "set_if_above": 85,
            "labels": [
                "not_attack",
                "attack"
            ],
            "label_values": [
                0,
                1
            ]
        },
        "version": 1
    }

Prepare a Dataset using Curl
----------------------------

::

    auth_header="Authorization: JWT ${token}"
    curl -s -X POST \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --header "${auth_header}" \
        -d '{ "title": "Prepare new Dataset from recordings", "desc": "", "ds_name": "new_recording", "ds_glob_path": "/opt/datasets/*/*.csv", "ds_dir": "/opt/datasets", "full_file": "/tmp/fulldata_attack_scans.csv", "clean_file": "/tmp/cleaned_attack_scans.csv", "meta_suffix": "metadata.json", "output_dir": "/tmp/", "pipeline_files": { "attack_files": [] }, "meta_data": {}, "post_proc": { "drop_columns": [ "src_file", "raw_id", "raw_load", "raw_hex_load", "raw_hex_field_load", "pad_load", "eth_dst", "eth_src", "ip_dst", "ip_src" ], "predict_feature": "label_name" }, "label_rules": { "set_if_above": 85, "labels": [ "not_attack", "attack" ], "label_values": [ 0, 1 ] }, "version": 1 }' \
        'http://0.0.0.0:8080/mlprepare/'

    {"id":1,"user_id":1,"user_name":"root","status":"initial","control_state":"active","title":"Prepare new Dataset from recordings","desc":"no desc","full_file":"/tmp/fulldata_attack_scans.csv","clean_file":"/tmp/cleaned_attack_scans.csv","meta_suffix":"metadata.json","output_dir":"/tmp/","ds_dir":"/opt/datasets","ds_glob_path":"/opt/datasets/*/*.csv","pipeline_files":{"attack_files":[]},"post_proc":{"drop_columns":["src_file","raw_id","raw_load","raw_hex_load","raw_hex_field_load","pad_load","eth_dst","eth_src","ip_dst","ip_src"],"predict_feature":"label_name"},"label_rules":{"set_if_above":85,"labels":["not_attack","attack"],"label_values":[0,1]},"tracking_id":"prep_fcd155e3-bd99-46a5-86d9-957fc7a95a8a","version":1,"created":"2018-03-30 16:06:49","updated":"2018-03-30 16:06:49","deleted":""}

Check the Newly Prepared Dataset Files Exist
--------------------------------------------

::

    ls -l /tmp/*.csv
    -rw-r--r-- 1 jay jay   145580 Mar 30 09:07 /tmp/cleaned_attack_scans.csv
    -rw-r--r-- 1 jay jay 26478291 Mar 30 09:07 /tmp/fulldata_attack_scans.csv

There is also metadata and dataset debugging information in the created JSON files:

::

     ls -l /tmp/*.json
     -rw-r--r-- 1 jay jay 1498 Mar 30 09:07 /tmp/cleaned_metadata.json
     -rw-r--r-- 1 jay jay 2669 Mar 30 09:07 /tmp/fulldata_metadata.json

Get Prepared Dataset Record from the Database using Curl
--------------------------------------------------------

::

    auth_header="Authorization: JWT ${token}"
    curl -s -X GET \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --header "${auth_header}" \
        'http://0.0.0.0:8080/mlprepare/1/'

    {"id":1,"user_id":1,"user_name":"root","status":"finished","control_state":"finished","title":"Prepare new Dataset from recordings","desc":"no desc","full_file":"/tmp/fulldata_attack_scans.csv","clean_file":"/tmp/cleaned_attack_scans.csv","meta_suffix":"metadata.json","output_dir":"/tmp/","ds_dir":"/opt/datasets","ds_glob_path":"/opt/datasets/*/*.csv","pipeline_files":["/opt/datasets/react-redux/netdata-2018-01-29-13-36-35.csv","/opt/datasets/spring/netdata-2018-01-29-15-00-12.csv","/opt/datasets/vue/netdata-2018-01-29-14-12-44.csv","/opt/datasets/django/netdata-2018-01-28-23-12-13.csv","/opt/datasets/django/netdata-2018-01-28-23-06-05.csv","/opt/datasets/flask-restplus/netdata-2018-01-29-11-30-02.csv"],"post_proc":{"drop_columns":["src_file","raw_id","raw_load","raw_hex_load","raw_hex_field_load","pad_load","eth_dst","eth_src","ip_dst","ip_src"],"ignore_features":["label_name","src_file","raw_id","raw_load","raw_hex_field_load","pad_load","eth_dst","eth_src","ip_dst","ip_src"],"predict_feature":"label_name","feature_to_predict":"label_name","features_to_process":["arp_id","dns_id","eth_id","eth_type","icmp_id","idx","ip_id","ip_ihl","ip_len","ip_tos","ip_version","ipvsix_id","label_value","pad_id","tcp_dport","tcp_fields_options.MSS","tcp_fields_options.NOP","tcp_fields_options.SAckOK","tcp_fields_options.Timestamp","tcp_fields_options.WScale","tcp_id","tcp_seq","tcp_sport","udp_id","label_name"]},"label_rules":{"labels":["not_attack","attack"],"label_values":[0,1],"set_if_above":85},"tracking_id":"prep_fcd155e3-bd99-46a5-86d9-957fc7a95a8a","version":1,"created":"2018-03-30 16:06:49","updated":"2018-03-30 16:07:07","deleted":""}

Train a Deep Neural Network with a Dataset
==========================================

If you want to use the `AntiNex Datasets repository`_ you will need to clone the repository locally.

.. _AntiNex Datasets repository: https://github.com/jay-johnson/antinex-datasets

::

    git clone https://github.com/jay-johnson/antinex-datasets /opt/antinex-datasets

Here is the full HTTP request for training a new Deep Neural Network from a dataset on disk:

::

    {
        "label": "Full-Django-AntiNex-Simple-Scaler-DNN",
        "dataset": "/opt/antinex-datasets/v1/webapps/django/training-ready/v1_django_cleaned.csv",
        "ml_type": "classification",
        "publish_to_core": true,
        "predict_feature": "label_value",
        "features_to_process": [
            "idx",
            "arp_hwlen",
            "arp_hwtype",
            "arp_id",
            "arp_op",
            "arp_plen",
            "arp_ptype",
            "dns_default_aa",
            "dns_default_ad",
            "dns_default_an",
            "dns_default_ancount",
            "dns_default_ar",
            "dns_default_arcount",
            "dns_default_cd",
            "dns_default_id",
            "dns_default_length",
            "dns_default_ns",
            "dns_default_nscount",
            "dns_default_opcode",
            "dns_default_qd",
            "dns_default_qdcount",
            "dns_default_qr",
            "dns_default_ra",
            "dns_default_rcode",
            "dns_default_rd",
            "dns_default_tc",
            "dns_default_z",
            "dns_id",
            "eth_id",
            "eth_type",
            "icmp_addr_mask",
            "icmp_code",
            "icmp_gw",
            "icmp_id",
            "icmp_ptr",
            "icmp_seq",
            "icmp_ts_ori",
            "icmp_ts_rx",
            "icmp_ts_tx",
            "icmp_type",
            "icmp_unused",
            "ip_id",
            "ip_ihl",
            "ip_len",
            "ip_tos",
            "ip_version",
            "ipv6_fl",
            "ipv6_hlim",
            "ipv6_nh",
            "ipv6_plen",
            "ipv6_tc",
            "ipv6_version",
            "ipvsix_id",
            "pad_id",
            "tcp_dport",
            "tcp_fields_options.MSS",
            "tcp_fields_options.NOP",
            "tcp_fields_options.SAckOK",
            "tcp_fields_options.Timestamp",
            "tcp_fields_options.WScale",
            "tcp_id",
            "tcp_seq",
            "tcp_sport",
            "udp_dport",
            "udp_id",
            "udp_len",
            "udp_sport"
        ],
        "ignore_features": [
        ],
        "sort_values": [
        ],
        "seed": 42,
        "test_size": 0.2,
        "batch_size": 32,
        "epochs": 15,
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
                    "num_neurons": 200,
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

Train a Deep Neural Network with Curl
-------------------------------------

This example created Deep Neural Network by Job ID **3** with Results ID **3**.

::

    auth_header="Authorization: JWT ${token}"
    curl -s -X POST \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --header "${auth_header}" \
        -d '{ "label": "Full-Django-AntiNex-Simple-Scaler-DNN", "dataset": "/opt/antinex-datasets/v1/webapps/django/training-ready/v1_django_cleaned.csv", "ml_type": "classification", "publish_to_core": true, "predict_feature": "label_value", "features_to_process": [ "idx", "arp_hwlen", "arp_hwtype", "arp_id", "arp_op", "arp_plen", "arp_ptype", "dns_default_aa", "dns_default_ad", "dns_default_an", "dns_default_ancount", "dns_default_ar", "dns_default_arcount", "dns_default_cd", "dns_default_id", "dns_default_length", "dns_default_ns", "dns_default_nscount", "dns_default_opcode", "dns_default_qd", "dns_default_qdcount", "dns_default_qr", "dns_default_ra", "dns_default_rcode", "dns_default_rd", "dns_default_tc", "dns_default_z", "dns_id", "eth_id", "eth_type", "icmp_addr_mask", "icmp_code", "icmp_gw", "icmp_id", "icmp_ptr", "icmp_seq", "icmp_ts_ori", "icmp_ts_rx", "icmp_ts_tx", "icmp_type", "icmp_unused", "ip_id", "ip_ihl", "ip_len", "ip_tos", "ip_version", "ipv6_fl", "ipv6_hlim", "ipv6_nh", "ipv6_plen", "ipv6_tc", "ipv6_version", "ipvsix_id", "pad_id", "tcp_dport", "tcp_fields_options.MSS", "tcp_fields_options.NOP", "tcp_fields_options.SAckOK", "tcp_fields_options.Timestamp", "tcp_fields_options.WScale", "tcp_id", "tcp_seq", "tcp_sport", "udp_dport", "udp_id", "udp_len", "udp_sport" ], "ignore_features": [ ], "sort_values": [ ], "seed": 42, "test_size": 0.2, "batch_size": 32, "epochs": 15, "num_splits": 2, "loss": "binary_crossentropy", "optimizer": "adam", "metrics": [ "accuracy" ], "histories": [ "val_loss", "val_acc", "loss", "acc" ], "model_desc": { "layers": [ { "num_neurons": 200, "init": "uniform", "activation": "relu" }, { "num_neurons": 1, "init": "uniform", "activation": "sigmoid" } ] }, "label_rules": { "labels": [ "not_attack", "not_attack", "attack" ], "label_values": [ -1, 0, 1 ] }, "version": 1 }' \
        'http://0.0.0.0:8080/ml/'

    {"job":{"id":3,"user_id":1,"user_name":"root","title":"Full-Django-AntiNex-Simple-Scaler-DNN","desc":null,"ds_name":"Full-Django-AntiNex-Simple-Scaler-DNN","algo_name":"Full-Django-AntiNex-Simple-Scaler-DNN","ml_type":"classification","status":"initial","control_state":"active","predict_feature":"label_value","predict_manifest":{"job_id":3,"result_id":3,"ml_type":"classification","test_size":0.2,"epochs":15,"batch_size":32,"num_splits":2,"loss":"binary_crossentropy","metrics":["accuracy"],"optimizer":"adam","histories":["val_loss","val_acc","loss","acc"],"seed":42,"training_data":{},"csv_file":null,"meta_file":null,"use_model_name":"Full-Django-AntiNex-Simple-Scaler-DNN","dataset":"/opt/antinex-datasets/v1/webapps/django/training-ready/v1_django_cleaned.csv","predict_rows":null,"apply_scaler":true,"predict_feature":"label_value","features_to_process":["idx","arp_hwlen","arp_hwtype","arp_id","arp_op","arp_plen","arp_ptype","dns_default_aa","dns_default_ad","dns_default_an","dns_default_ancount","dns_default_ar","dns_default_arcount","dns_default_cd","dns_default_id","dns_default_length","dns_default_ns","dns_default_nscount","dns_default_opcode","dns_default_qd","dns_default_qdcount","dns_default_qr","dns_default_ra","dns_default_rcode","dns_default_rd","dns_default_tc","dns_default_z","dns_id","eth_id","eth_type","icmp_addr_mask","icmp_code","icmp_gw","icmp_id","icmp_ptr","icmp_seq","icmp_ts_ori","icmp_ts_rx","icmp_ts_tx","icmp_type","icmp_unused","ip_id","ip_ihl","ip_len","ip_tos","ip_version","ipv6_fl","ipv6_hlim","ipv6_nh","ipv6_plen","ipv6_tc","ipv6_version","ipvsix_id","pad_id","tcp_dport","tcp_fields_options.MSS","tcp_fields_options.NOP","tcp_fields_options.SAckOK","tcp_fields_options.Timestamp","tcp_fields_options.WScale","tcp_id","tcp_seq","tcp_sport","udp_dport","udp_id","udp_len","udp_sport"],"ignore_features":[],"sort_values":[],"model_desc":{"layers":[{"num_neurons":200,"init":"uniform","activation":"relu"},{"num_neurons":1,"init":"uniform","activation":"sigmoid"}]},"label_rules":{"labels":["not_attack","not_attack","attack"],"label_values":[-1,0,1]},"post_proc_rules":null,"model_weights_file":"/tmp/ml_weights_job_3_result_3.h5","verbose":1,"version":1,"publish_to_core":true,"worker_result_node":{"source":"drf","auth_url":"redis://localhost:6379/9","ssl_options":{},"exchange":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","exchange_type":"topic","routing_key":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","queue":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","delivery_mode":2,"task_name":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","manifest":{"job_id":3,"result_id":3,"job_type":"train-and-predict"}}},"training_data":{},"pre_proc":{},"post_proc":{},"meta_data":{},"tracking_id":"ml_4529bda5-2003-45ce-b08b-bfc48d6a008b","version":1,"created":"2018-03-30 16:25:49","updated":"2018-03-30 16:25:49","deleted":""},"results":{"id":3,"user_id":1,"user_name":"root","job_id":3,"status":"initial","test_size":0.2,"csv_file":null,"meta_file":null,"version":1,"acc_data":{"accuracy":-1.0},"error_data":null,"model_json":null,"model_weights":null,"acc_image_file":null,"predictions_json":null,"created":"2018-03-30 16:25:49","updated":"2018-03-30 16:25:49","deleted":""}}

Get a Deep Neural Network Job Record with Curl
----------------------------------------------

Get the example Deep Neural Network Job by ID **3**.

::

    auth_header="Authorization: JWT ${token}"
    curl -s -X GET \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --header "${auth_header}" \
        'http://0.0.0.0:8080/ml/3/'

    {"id":3,"user_id":1,"user_name":"root","title":"Full-Django-AntiNex-Simple-Scaler-DNN","desc":null,"ds_name":"Full-Django-AntiNex-Simple-Scaler-DNN","algo_name":"Full-Django-AntiNex-Simple-Scaler-DNN","ml_type":"classification","status":"finished","control_state":"finished","predict_feature":"label_value","predict_manifest":{"loss":"binary_crossentropy","seed":42,"epochs":15,"job_id":3,"dataset":"/opt/antinex-datasets/v1/webapps/django/training-ready/v1_django_cleaned.csv","metrics":["accuracy"],"ml_type":"classification","verbose":1,"version":1,"csv_file":null,"histories":["val_loss","val_acc","loss","acc"],"meta_file":null,"optimizer":"adam","result_id":3,"test_size":0.2,"batch_size":32,"model_desc":{"layers":[{"init":"uniform","activation":"relu","num_neurons":200},{"init":"uniform","activation":"sigmoid","num_neurons":1}]},"num_splits":2,"label_rules":{"labels":["not_attack","not_attack","attack"],"label_values":[-1,0,1]},"sort_values":[],"apply_scaler":true,"predict_rows":null,"training_data":{},"use_model_name":"Full-Django-AntiNex-Simple-Scaler-DNN","ignore_features":[],"post_proc_rules":null,"predict_feature":"label_value","publish_to_core":true,"model_weights_file":"/tmp/ml_weights_job_3_result_3.h5","worker_result_node":{"queue":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","source":"drf","auth_url":"redis://localhost:6379/9","exchange":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","manifest":{"job_id":3,"job_type":"train-and-predict","result_id":3},"task_name":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","routing_key":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","ssl_options":{},"delivery_mode":2,"exchange_type":"topic"},"features_to_process":["idx","arp_hwlen","arp_hwtype","arp_id","arp_op","arp_plen","arp_ptype","dns_default_aa","dns_default_ad","dns_default_an","dns_default_ancount","dns_default_ar","dns_default_arcount","dns_default_cd","dns_default_id","dns_default_length","dns_default_ns","dns_default_nscount","dns_default_opcode","dns_default_qd","dns_default_qdcount","dns_default_qr","dns_default_ra","dns_default_rcode","dns_default_rd","dns_default_tc","dns_default_z","dns_id","eth_id","eth_type","icmp_addr_mask","icmp_code","icmp_gw","icmp_id","icmp_ptr","icmp_seq","icmp_ts_ori","icmp_ts_rx","icmp_ts_tx","icmp_type","icmp_unused","ip_id","ip_ihl","ip_len","ip_tos","ip_version","ipv6_fl","ipv6_hlim","ipv6_nh","ipv6_plen","ipv6_tc","ipv6_version","ipvsix_id","pad_id","tcp_dport","tcp_fields_options.MSS","tcp_fields_options.NOP","tcp_fields_options.SAckOK","tcp_fields_options.Timestamp","tcp_fields_options.WScale","tcp_id","tcp_seq","tcp_sport","udp_dport","udp_id","udp_len","udp_sport"]},"training_data":{},"pre_proc":{},"post_proc":{},"meta_data":{},"tracking_id":"ml_4529bda5-2003-45ce-b08b-bfc48d6a008b","version":1,"created":"2018-03-30 16:25:49","updated":"2018-03-30 16:26:49","deleted":""}

Get a Deep Neural Network Results with Curl
-------------------------------------------

Get the example Deep Neural Network Training, Accuracy and Prediction Results by ID **3**.

.. note:: This will return all **30200** records so it can take a second

::

    auth_header="Authorization: JWT ${token}"
    curl -s -X GET \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --header "${auth_header}" \
        'http://0.0.0.0:8080/mlresults/3/'

    ...

    {"id":3,"user_id":1,"user_name":"root","job_id":3,"status":"finished","test_size":0.2,"csv_file":null,"meta_file":null,"version":1,"acc_data":{"accuracy":99.82615894039735},"error_data":null,"model_json":"{\"class_name\": \"Sequential\", \"config\": [{\"class_name\": \"Dense\", \"config\": {\"name\": \"dense_1\", \"trainable\": true, \"batch_input_shape\": [null, 67], \"dtype\": \"float32\", \"units\": 200, \"activation\": \"relu\", \"use_bias\": true, \"kernel_initializer\": {\"class_name\": \"RandomUniform\", \"config\": {\"minval\": -0.05, \"maxval\": 0.05, \"seed\": null}}, \"bias_initializer\": {\"class_name\": \"Zeros\", \"config\": {}}, \"kernel_regularizer\": null, \"bias_regularizer\": null, \"activity_regularizer\": null, \"kernel_constraint\": null, \"bias_constraint\": null}}, {\"class_name\": \"Dense\", \"config\": {\"name\": \"dense_2\", \"trainable\": true, \"units\": 1, \"activation\": \"sigmoid\", \"use_bias\": true, \"kernel_initializer\": {\"class_name\": \"RandomUniform\", \"config\": {\"minval\": -0.05, \"maxval\": 0.05, \"seed\": null}}, \"bias_initializer\": {\"class_name\": \"Zeros\", \"config\": {}}, \"kernel_regularizer\": null, \"bias_regularizer\": null, \"activity_regularizer\": null, \"kernel_constraint\": null, \"bias_constraint\": null}}], \"keras_version\": \"2.1.5\", \"backend\": \"tensorflow\"}","model_weights":{},"acc_image_file":null,"predictions_json":{"predictions":[

    ... lots of prediction dictionaries
    
Make New Predictions with a Pre-trained Deep Neural Network with Curl
---------------------------------------------------------------------

This example uses the pre-trained Deep Neural Network to make new predictions with a Job ID **4** with Results ID **4**.

::

    auth_header="Authorization: JWT ${token}"
    curl -s -X POST \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --header "${auth_header}" \
        -d '{ "label": "Full-Django-AntiNex-Simple-Scaler-DNN", "dataset": "/opt/antinex-datasets/v1/webapps/django/training-ready/v1_django_cleaned.csv", "ml_type": "classification", "publish_to_core": true, "predict_feature": "label_value", "features_to_process": [ "idx", "arp_hwlen", "arp_hwtype", "arp_id", "arp_op", "arp_plen", "arp_ptype", "dns_default_aa", "dns_default_ad", "dns_default_an", "dns_default_ancount", "dns_default_ar", "dns_default_arcount", "dns_default_cd", "dns_default_id", "dns_default_length", "dns_default_ns", "dns_default_nscount", "dns_default_opcode", "dns_default_qd", "dns_default_qdcount", "dns_default_qr", "dns_default_ra", "dns_default_rcode", "dns_default_rd", "dns_default_tc", "dns_default_z", "dns_id", "eth_id", "eth_type", "icmp_addr_mask", "icmp_code", "icmp_gw", "icmp_id", "icmp_ptr", "icmp_seq", "icmp_ts_ori", "icmp_ts_rx", "icmp_ts_tx", "icmp_type", "icmp_unused", "ip_id", "ip_ihl", "ip_len", "ip_tos", "ip_version", "ipv6_fl", "ipv6_hlim", "ipv6_nh", "ipv6_plen", "ipv6_tc", "ipv6_version", "ipvsix_id", "pad_id", "tcp_dport", "tcp_fields_options.MSS", "tcp_fields_options.NOP", "tcp_fields_options.SAckOK", "tcp_fields_options.Timestamp", "tcp_fields_options.WScale", "tcp_id", "tcp_seq", "tcp_sport", "udp_dport", "udp_id", "udp_len", "udp_sport" ], "ignore_features": [ ], "sort_values": [ ], "seed": 42, "test_size": 0.2, "batch_size": 32, "epochs": 15, "num_splits": 2, "loss": "binary_crossentropy", "optimizer": "adam", "metrics": [ "accuracy" ], "histories": [ "val_loss", "val_acc", "loss", "acc" ], "model_desc": { "layers": [ { "num_neurons": 200, "init": "uniform", "activation": "relu" }, { "num_neurons": 1, "init": "uniform", "activation": "sigmoid" } ] }, "label_rules": { "labels": [ "not_attack", "not_attack", "attack" ], "label_values": [ -1, 0, 1 ] }, "version": 1 }' \
        'http://0.0.0.0:8080/ml/'

    {"job":{"id":4,"user_id":1,"user_name":"root","title":"Full-Django-AntiNex-Simple-Scaler-DNN","desc":null,"ds_name":"Full-Django-AntiNex-Simple-Scaler-DNN","algo_name":"Full-Django-AntiNex-Simple-Scaler-DNN","ml_type":"classification","status":"initial","control_state":"active","predict_feature":"label_value","predict_manifest":{"job_id":4,"result_id":4,"ml_type":"classification","test_size":0.2,"epochs":15,"batch_size":32,"num_splits":2,"loss":"binary_crossentropy","metrics":["accuracy"],"optimizer":"adam","histories":["val_loss","val_acc","loss","acc"],"seed":42,"training_data":{},"csv_file":null,"meta_file":null,"use_model_name":"Full-Django-AntiNex-Simple-Scaler-DNN","dataset":"/opt/antinex-datasets/v1/webapps/django/training-ready/v1_django_cleaned.csv","predict_rows":null,"apply_scaler":true,"predict_feature":"label_value","features_to_process":["idx","arp_hwlen","arp_hwtype","arp_id","arp_op","arp_plen","arp_ptype","dns_default_aa","dns_default_ad","dns_default_an","dns_default_ancount","dns_default_ar","dns_default_arcount","dns_default_cd","dns_default_id","dns_default_length","dns_default_ns","dns_default_nscount","dns_default_opcode","dns_default_qd","dns_default_qdcount","dns_default_qr","dns_default_ra","dns_default_rcode","dns_default_rd","dns_default_tc","dns_default_z","dns_id","eth_id","eth_type","icmp_addr_mask","icmp_code","icmp_gw","icmp_id","icmp_ptr","icmp_seq","icmp_ts_ori","icmp_ts_rx","icmp_ts_tx","icmp_type","icmp_unused","ip_id","ip_ihl","ip_len","ip_tos","ip_version","ipv6_fl","ipv6_hlim","ipv6_nh","ipv6_plen","ipv6_tc","ipv6_version","ipvsix_id","pad_id","tcp_dport","tcp_fields_options.MSS","tcp_fields_options.NOP","tcp_fields_options.SAckOK","tcp_fields_options.Timestamp","tcp_fields_options.WScale","tcp_id","tcp_seq","tcp_sport","udp_dport","udp_id","udp_len","udp_sport"],"ignore_features":[],"sort_values":[],"model_desc":{"layers":[{"num_neurons":200,"init":"uniform","activation":"relu"},{"num_neurons":1,"init":"uniform","activation":"sigmoid"}]},"label_rules":{"labels":["not_attack","not_attack","attack"],"label_values":[-1,0,1]},"post_proc_rules":null,"model_weights_file":"/tmp/ml_weights_job_4_result_4.h5","verbose":1,"version":1,"publish_to_core":true,"worker_result_node":{"source":"drf","auth_url":"redis://localhost:6379/9","ssl_options":{},"exchange":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","exchange_type":"topic","routing_key":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","queue":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","delivery_mode":2,"task_name":"drf_network_pipeline.pipeline.tasks.task_ml_process_results","manifest":{"job_id":4,"result_id":4,"job_type":"train-and-predict"}}},"training_data":{},"pre_proc":{},"post_proc":{},"meta_data":{},"tracking_id":"ml_cb723821-e840-45ad-ac3a-94a86a0cfc88","version":1,"created":"2018-03-30 16:32:56","updated":"2018-03-30 16:32:56","deleted":""},"results":{"id":4,"user_id":1,"user_name":"root","job_id":4,"status":"initial","test_size":0.2,"csv_file":null,"meta_file":null,"version":1,"acc_data":{"accuracy":-1.0},"error_data":null,"model_json":null,"model_weights":null,"acc_image_file":null,"predictions_json":null,"created":"2018-03-30 16:32:56","updated":"2018-03-30 16:32:56","deleted":""}}

Get New Predictions Results from the Pre-trained Deep Neural Network with Curl
------------------------------------------------------------------------------

Get the example Deep Neural Network Training, Accuracy and Prediction Results by ID **4**.

.. note:: This will return all **30200** records so it can take a second

::

    auth_header="Authorization: JWT ${token}"
    curl -s -X GET \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --header "${auth_header}" \
        'http://0.0.0.0:8080/mlresults/4/'

    ...


    {"id":4,"user_id":1,"user_name":"root","job_id":4,"status":"finished","test_size":0.2,"csv_file":null,"meta_file":null,"version":1,"acc_data":{"accuracy":99.82615894039735},"error_data":null,"model_json":"{\"class_name\": \"Sequential\", \"config\": [{\"class_name\": \"Dense\", \"config\": {\"name\": \"dense_1\", \"trainable\": true, \"batch_input_shape\": [null, 67], \"dtype\": \"float32\", \"units\": 200, \"activation\": \"relu\", \"use_bias\": true, \"kernel_initializer\": {\"class_name\": \"RandomUniform\", \"config\": {\"minval\": -0.05, \"maxval\": 0.05, \"seed\": null}}, \"bias_initializer\": {\"class_name\": \"Zeros\", \"config\": {}}, \"kernel_regularizer\": null, \"bias_regularizer\": null, \"activity_regularizer\": null, \"kernel_constraint\": null, \"bias_constraint\": null}}, {\"class_name\": \"Dense\", \"config\": {\"name\": \"dense_2\", \"trainable\": true, \"units\": 1, \"activation\": \"sigmoid\", \"use_bias\": true, \"kernel_initializer\": {\"class_name\": \"RandomUniform\", \"config\": {\"minval\": -0.05, \"maxval\": 0.05, \"seed\": null}}, \"bias_initializer\": {\"class_name\": \"Zeros\", \"config\": {}}, \"kernel_regularizer\": null, \"bias_regularizer\": null, \"activity_regularizer\": null, \"kernel_constraint\": null, \"bias_constraint\": null}}], \"keras_version\": \"2.1.5\", \"backend\": \"tensorflow\"}","model_weights":{},"acc_image_file":null,"predictions_json":{"predictions":[

    ... lots of prediction dictionaries
    
Using Python Scripts
--------------------

There are many example scripts through the repositories that use python to interface with each of the AntiNex components.

Here are some links to additional, more up-to-date examples:

https://github.com/jay-johnson/train-ai-with-django-swagger-jwt#automation

https://github.com/jay-johnson/antinex-core#publish-a-predict-request

https://github.com/jay-johnson/antinex-client#run-predictions

Debugging
=========

Tail the API logs
-----------------

From the base directory of the `Django REST API repository`_ you can watch what the server is doing inside the container with:

::

    ./tail-api.sh

Tail the Celery Worker logs
---------------------------

From the base directory of the `Django REST API repository`_ you can watch what the REST API Celery Worker is doing inside the container with:

::

    ./tail-worker.sh

Tail the AntiNex Core Worker logs
---------------------------------

From the base directory of the `Django REST API repository`_ you can watch what the AntiNex Core Worker (which is also a Celery Worker) is doing inside the container with:

::

    ./tail-core.sh

Signature has expired
---------------------

Log back in to get a new token if you see this message:

::

    {"detail":"Signature has expired."}

::

    token=$(curl -s -X POST \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/json' \
    -d '{ "username": "root", "password": "123321" }' \
    'http://0.0.0.0:8080/api-token-auth/' \
    | sed -e 's/"/ /g' | awk '{print $4}')
        
.. _Django REST API repository: https://github.com/jay-johnson/train-ai-with-django-swagger-jwt
