import os
import logging
import uuid
import json
import pandas as pd
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from rest_framework import serializers
from rest_framework import status as drf_status
from celery_connectors.utils import ev
from network_pipeline.log.setup_logging import setup_logging
from network_pipeline.utils import ppj
from network_pipeline.consts import VALID
from network_pipeline.build_training_request import build_training_request
from drf_network_pipeline.pipeline.consts import SUCCESS
from drf_network_pipeline.pipeline.consts import FAILED
from drf_network_pipeline.pipeline.consts import ERR
from drf_network_pipeline.sz.user import UserSerializer
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.pipeline.prepare_dataset_tools import \
    build_csv
from drf_network_pipeline.pipeline.prepare_dataset_tools import \
    find_all_pipeline_csvs
from drf_network_pipeline.pipeline.models import MLJobResult
from keras.models import Sequential
from keras.layers import Dense
from keras import backend as K


setup_logging()
name = "ml-sz"
log = logging.getLogger(name)


User = get_user_model()  # noqa


class MLPrepareSerializer(serializers.Serializer):

    title = serializers.CharField(
                max_length=256,
                required=False,
                default=None)
    desc = serializers.CharField(
                max_length=1024,
                required=False,
                default=None)
    full_file = serializers.CharField(
                max_length=1024,
                allow_blank=False,
                default="/tmp/fulldata_attack_scans.csv")
    clean_file = serializers.CharField(
                max_length=1024,
                allow_blank=False,
                default="/tmp/cleaned_attack_scans.csv")
    meta_prefix = serializers.CharField(
                max_length=256,
                allow_blank=False,
                default="metadata")
    output_dir = serializers.CharField(
                max_length=1024,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="/tmp")
    ds_dir = serializers.CharField(
                max_length=1024,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="/opt/datasets")
    ds_glob_path = serializers.CharField(
                max_length=1024,
                min_length=None,
                allow_blank=False,
                default="/opt/datasets/*/*.csv")
    pipeline_files = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    post_proc = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    label_rules = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    meta_data = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    version = serializers.IntegerField(
                default=1,
                required=False)

    request = None
    class_name = "MLPrepare"

    class Meta:
        fields = (
            "id",
            "status",
            "control_state",
            "title",
            "desc",
            "full_file",
            "clean_file",
            "meta_prefix",
            "output_dir",
            "ds_dir",
            "ds_glob_path",
            "pipeline_files",
            "post_proc",
            "label_rules",
            "meta_data",
            "version",
        )

    def create(self,
               request,
               validated_data):
        """create

        Start a new Prepare Job

        :param request: http request
        :param validated_data: post dictionary
        """

        last_step = ""
        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:

            user_id = request.user.id

            log.info(("{} create user_id={} data={}")
                     .format(self.class_name,
                             user_id,
                             validated_data))

            status = "initial"
            control_state = "active"
            title = "no title"
            desc = "no desc"
            full_file = None
            clean_file = None
            meta_prefix = None
            output_dir = None
            ds_dir = None
            ds_glob_path = None
            pipeline_files = None
            post_proc = None
            label_rules = None
            meta_data = None
            version = 1

            if validated_data["title"]:
                title = validated_data["title"]
            if validated_data["desc"]:
                desc = validated_data["desc"]
            if validated_data["full_file"]:
                last_step = "parsing full_file"
                full_file = validated_data["full_file"]
            if validated_data["clean_file"]:
                last_step = "parsing clean_file"
                clean_file = validated_data["clean_file"]
            if validated_data["meta_prefix"]:
                last_step = "parsing meta_prefix"
                meta_prefix = validated_data["meta_prefix"]
            if validated_data["output_dir"]:
                last_step = "parsing output_dir"
                output_dir = validated_data["output_dir"]
            if validated_data["ds_dir"]:
                last_step = "parsing ds_dir"
                ds_dir = validated_data["ds_dir"]
            if validated_data["ds_glob_path"]:
                last_step = "parsing ds_glob_path"
                ds_glob_path = validated_data["ds_glob_path"]
            if validated_data["pipeline_files"]:
                last_step = "parsing pipeline_files"
                pipeline_files = json.loads(validated_data["pipeline_files"])
            if validated_data["post_proc"]:
                last_step = "parsing meta_data"
                post_proc = json.loads(validated_data["post_proc"])
            if validated_data["meta_data"]:
                last_step = "parsing meta_data"
                meta_data = json.loads(validated_data["meta_data"])
            if validated_data["label_rules"]:
                last_step = "parsing label_rules"
                label_rules = json.loads(validated_data["label_rules"])
            if validated_data["version"]:
                version = int(validated_data["version"])

            tracking_id = "prep_{}".format(
                            str(uuid.uuid4()))

            obj = MLPrepare(
                    user=request.user,
                    status=status,
                    control_state=control_state,
                    title=title,
                    desc=desc,
                    full_file=full_file,
                    clean_file=clean_file,
                    meta_prefix=meta_prefix,
                    output_dir=output_dir,
                    ds_dir=ds_dir,
                    ds_glob_path=ds_glob_path,
                    pipeline_files=pipeline_files,
                    post_proc=post_proc,
                    label_rules=label_rules,
                    meta_data=meta_data,
                    tracking_id=tracking_id,
                    version=version)

            last_step = "saving"
            log.info("saving prepare")
            obj.save()

            last_step = ("starting user={} prepare={} "
                         "pipeline={} clean={} full={} "
                         "post={} label={} tracking={}").format(
                             user_id,
                             obj.id,
                             pipeline_files,
                             clean_file,
                             full_file,
                             post_proc,
                             label_rules,
                             tracking_id)
            log.info(last_step)

            log.info(("prepare={} csvs={}")
                     .format(obj.id,
                             ds_glob_path))

            pipeline_files = find_all_pipeline_csvs(
                                csv_glob_path=ds_glob_path)

            post_proc_rules = {
                "drop_columns": [
                    "src_file",
                    "raw_id",
                    "raw_load",
                    "raw_hex_load",
                    "raw_hex_field_load",
                    "pad_load",
                    "eth_dst",  # need to make this an int
                    "eth_src",  # need to make this an int
                    "ip_dst",   # need to make this an int
                    "ip_src"    # need to make this an int
                ],
                "predict_feature": "label_name"
            }

            label_rules = {
                "set_if_above": 85,
                "labels": ["not_attack", "attack"],
                "label_values": [0, 1]
            }

            log.info(("preparing={} clean={} full={} "
                      "files={}")
                     .format(obj.id,
                             clean_file,
                             full_file,
                             pipeline_files))

            save_node = build_csv(
                pipeline_files=pipeline_files,
                fulldata_file=full_file,
                clean_file=clean_file,
                post_proc_rules=post_proc_rules,
                label_rules=label_rules)

            if save_node["status"] == VALID:

                log.info("successfully process datasets:")

                obj.post_proc = save_node["post_proc_rules"]
                obj.post_proc["features_to_process"] = \
                    save_node["features_to_process"]
                obj.post_proc["ignore_features"] = \
                    save_node["ignore_features"]
                obj.post_proc["feature_to_predict"] = \
                    save_node["feature_to_predict"]
                obj.label_rules = save_node["label_rules"]
                obj.pipeline_files = save_node["pipeline_files"]
                obj.full_file = save_node["fulldata_file"]
                obj.clean_file = save_node["clean_file"]
                obj.status = "finished"
                obj.control_state = "finished"
                obj.save()
                log.info(("saved prepare={}")
                         .format(obj.id))

                if ev("SHOW_SUMMARY",
                      "0") == "1":
                    log.info(("Full csv: {}")
                             .format(save_node["fulldata_file"]))
                    log.info(("Full meta: {}")
                             .format(save_node["fulldata_metadata_file"]))
                    log.info(("Clean csv: {}")
                             .format(save_node["clean_file"]))
                    log.info(("Clean meta: {}")
                             .format(save_node["clean_metadata_file"]))
                    log.info("------------------------------------------")
                    log.info(("Predicting Feature: {}")
                             .format(save_node["feature_to_predict"]))
                    log.info(("Features to Process: {}")
                             .format(ppj(save_node["features_to_process"])))
                    log.info(("Ignored Features: {}")
                             .format(ppj(save_node["ignore_features"])))
                    log.info("------------------------------------------")
                # end of show summary

                log.info("Full: {}".format(
                    save_node["fulldata_file"]))
                log.info("Cleaned (no-NaNs in columns): {}".format(
                    save_node["clean_file"]))
                data = obj.get_public()
                res = {
                    "status": SUCCESS,
                    "code": drf_status.HTTP_201_CREATED,
                    "error": "",
                    "data": data
                }
            else:
                last_step = ("failed to prepare csv status={} "
                             "errors: {}").format(
                                save_node["status"],
                                save_node["err"])
                log.error(last_step)
                obj.status = "error"
                obj.control_state = "error"
                obj.save()
                data["prepare"] = obj.get_public()
                data["ready"] = {}
                res = {
                    "status": ERR,
                    "code": drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": last_step,
                    "data": data
                }
                return res
            # end of checking it started

        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} create res={}")
                 .format(self.class_name,
                         res))

        return res
    # end of create

    def update(self,
               request,
               pk=None):
        """update

        Update an MLPrepare

        :param request: http request
        :param pk: MLPrepare.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} update pk={}")
                     .format(self.class_name,
                             pk))

            res = {
                "status": SUCCESS,
                "code": drf_status.HTTP_200_OK,
                "error": "not implemented yet",
                "data": data
            }
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} update res={}")
                 .format(self.class_name,
                         res))

        return res
    # end of update

    def get(self,
            request,
            pk):
        """get

        Start a new MLPrepare

        :param request: http request
        :param pk: MLPrepare.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} get user_id={} pk={}")
                     .format(self.class_name,
                             request.user.id,
                             pk))

            db_query = (Q(user=request.user.id) & Q(id=pk))
            qset = []
            if pk:
                qset = MLPrepare.objects.select_related() \
                            .filter(db_query)
            else:
                db_query = (Q(user=request.user.id))
                qset = MLPrepare.objects.select_related().filter(
                        db_query).order_by(
                        "-created").all()[:settings.MAX_RECS_ML_JOB_RESULT]

            if len(qset) == 1:
                data = qset[0].get_public()
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""
            elif len(qset) > 1:
                data["prepares"] = []
                for i in qset:
                    data["prepares"].append(i.get_public())
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""
            else:
                data = {}
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""

            res["status"] = SUCCESS
            res["data"] = data
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} get res={}")
                 .format(self.class_name,
                         json.dumps(res)[0:32]))

        return res
    # end of get

    def delete(self,
               request,
               pk):
        """delete

        Delete an MLPrepare

        :param request: http request
        :param pk: MLPrepare.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} delete pk={}")
                     .format(self.class_name,
                             pk))

            res = {
                "status": SUCCESS,
                "code": drf_status.HTTP_200_OK,
                "error": "not implemented yet",
                "data": data
            }
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} delete res={}")
                 .format(self.class_name,
                         res))

        return res
    # end of delete

# end of MLPrepareSerializer


class MLJobsSerializer(serializers.Serializer):

    title = serializers.CharField(
                required=False,
                default=None)
    desc = serializers.CharField(
                required=False,
                default=None)
    csv_file = serializers.CharField(
                max_length=1024,
                allow_blank=False,
                required=True)
    meta_file = serializers.CharField(
                max_length=1024,
                allow_blank=False,
                required=True)
    ds_name = serializers.CharField(
                max_length=1024,
                allow_blank=False,
                required=True)
    algo_name = serializers.CharField(
                max_length=1024,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="")
    ml_type = serializers.CharField(
                max_length=256,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="Predict with Filter")
    status = serializers.CharField(
                max_length=256,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="initial")
    control_state = serializers.CharField(
                max_length=256,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="active")
    predict_feature = serializers.CharField(
                max_length=256,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="")
    training_data = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    pre_proc = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    post_proc = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    meta_data = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    tracking_id = serializers.CharField(
                max_length=512,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="")
    version = serializers.IntegerField(
                default=1,
                required=False)

    request = None
    class_name = "MLJob"

    class Meta:
        fields = (
            "id",
            "csv_file",
            "meta_file",
            "title",
            "desc",
            "ds_name",
            "algo_name",
            "ml_type",
            "status",
            "control_state",
            "predict_feature",
            "training_data",
            "pre_proc",
            "post_proc",
            "meta_data",
            "tracking_id",
            "version",
        )

    def create(self,
               request,
               validated_data):
        """create

        Start a new MLJob

        :param request: http request
        :param validated_data: post dictionary
        """

        last_step = ""
        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            user_id = request.user.id

            log.info(("{} create user_id={} data={}")
                     .format(self.class_name,
                             user_id,
                             validated_data))

            last_step = "parsing data"
            title = validated_data["title"]
            desc = validated_data["desc"]
            ds_name = validated_data["ds_name"]
            algo_name = validated_data["algo_name"]
            ml_type = validated_data["ml_type"]
            version = validated_data["version"]
            status = "initial"
            control_state = "active"
            predict_feature = validated_data["predict_feature"]
            training_data = json.loads(validated_data["training_data"])
            pre_proc = json.loads(validated_data["pre_proc"])
            post_proc = json.loads(validated_data["post_proc"])
            meta_data = json.loads(validated_data["meta_data"])
            tracking_id = "ml_{}".format(str(uuid.uuid4()))
            test_size = 0.20
            epochs = 5
            batch_size = 2
            verbose = 1

            if "test_size" in training_data:
                last_step = "parsing test_size"
                test_size = float(training_data["test_size"])
            if "epochs" in training_data:
                last_step = "parsing test_size"
                epochs = int(training_data["epochs"])
            if "batch_size" in training_data:
                last_step = "parsing batch_size"
                batch_size = int(training_data["batch_size"])
            if "verbose" in training_data:
                last_step = "parsing verbose"
                verbose = int(training_data["verbose"])

            csv_file = validated_data["csv_file"]
            meta_file = validated_data["meta_file"]

            if not os.path.exists(csv_file):
                last_step = ("Missing csv_file={}").format(
                                csv_file)
                log.error(last_step)
                res = {
                    "status": ERR,
                    "code": drf_status.HTTP_400_BAD_REQUEST,
                    "error": last_step,
                    "data": data
                }
                return res
            # end of check for csv file
            if not os.path.exists(meta_file):
                last_step = ("Missing meta_file={}").format(
                                csv_file)
                log.error(last_step)
                res = {
                    "status": ERR,
                    "code": drf_status.HTTP_400_BAD_REQUEST,
                    "error": last_step,
                    "data": data
                }
                return res
            # end of check for meta file

            job = MLJob(
                    user=request.user,
                    title=title,
                    desc=desc,
                    ds_name=ds_name,
                    algo_name=algo_name,
                    ml_type=ml_type,
                    status=status,
                    control_state=control_state,
                    predict_feature=predict_feature,
                    training_data=training_data,
                    pre_proc=pre_proc,
                    post_proc=post_proc,
                    meta_data=meta_data,
                    tracking_id=tracking_id,
                    version=version)

            last_step = "saving"
            log.info("saving job")
            job.save()

            last_step = ("starting user={} job={} "
                         "csv={} meta={}").format(
                             user_id,
                             job.id,
                             csv_file,
                             meta_file)
            log.info(last_step)

            ml_req = build_training_request(
                    csv_file=csv_file,
                    meta_file=meta_file,
                    predict_feature=predict_feature,
                    test_size=test_size)

            if ml_req["status"] != VALID:
                last_step = ("Stopping for status={} "
                             "errors: {}").format(
                                ml_req["status"],
                                ml_req["err"])
                log.error(last_step)
                job.status = "error"
                job.control_state = "error"
                log.info(("saving job={}")
                         .format(job.id))
                job.save()
                data["job"] = job.get_public()
                error_data = {
                    "status": ml_req["status"],
                    "err": ml_req["err"]
                }
                job_results = MLJobResult(
                    user=job.user,
                    job=job,
                    status="finished",
                    acc_data=None,
                    error_data=error_data)
                job_results.save()
                data["results"] = job_results.get_public()
                res = {
                    "status": ERR,
                    "code": drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": last_step,
                    "data": data
                }
                return res
            else:
                last_step = ("built_training_request={} "
                             "features={} ignore={}").format(
                                 ml_req["status"],
                                 ml_req["features_to_process"],
                                 ml_req["ignore_features"])

                log.info(last_step)

                log.info("resetting Keras backend")
                K.clear_session()

                log.info("creating Keras - sequential model")

                # create the model
                model = Sequential()
                model.add(Dense(8,
                                input_dim=len(ml_req["features_to_process"]),
                                kernel_initializer="uniform",
                                activation="relu"))
                model.add(Dense(6,
                                kernel_initializer="uniform",
                                activation="relu"))
                model.add(Dense(1,
                                kernel_initializer="uniform",
                                activation="sigmoid"))

                last_step = "compiling model"
                log.info(last_step)

                # compile the model
                model.compile(loss="binary_crossentropy",
                              optimizer="adam",
                              metrics=["accuracy"])

                last_step = ("fitting model - "
                             "epochs={} batch={} "
                             "verbose={} - please wait").format(
                                 epochs,
                                 batch_size,
                                 verbose)
                log.info(last_step)

                # fit the model
                model.fit(ml_req["X_train"],
                          ml_req["Y_train"],
                          validation_data=(ml_req["X_test"],
                                           ml_req["Y_test"]),
                          epochs=epochs,
                          batch_size=batch_size,
                          verbose=verbose)

                # evaluate the model
                scores = model.evaluate(ml_req["X_test"],
                                        ml_req["Y_test"])
                last_step = ("job={} accuracy={}").format(
                                job.id,
                                scores[1] * 100)
                log.info(last_step)

                db_query = (Q(user=user_id) & Q(id=job.id))
                qset = MLJob.objects.select_related() \
                            .filter(db_query)

                if len(qset) > 0:
                    last_step = "converting"
                    log.info(last_step)
                    data["job"] = qset[0].get_public()
                    job.status = "finished"
                    job.control_state = "finished"
                    job.save()
                    log.info(("saved job={}")
                             .format(job.id))

                    acc_data = {
                        "accuracy": scores[1] * 100
                    }
                    error_data = None
                    log.info(("converting job={} model to json")
                             .format(job.id))
                    model_json = model.to_json()
                    log.info(("converting job={} model weights")
                             .format(job.id))
                    model_weights = {
                        "weights": pd.Series(
                            model.get_weights()).to_json(
                                orient="values")
                    }
                    log.info(("saving job={} results")
                             .format(job.id))
                    job_results = MLJobResult(
                        user=job.user,
                        job=job,
                        status="finished",
                        acc_data=acc_data,
                        error_data=error_data,
                        model_json=model_json,
                        model_weights=model_weights,
                        version=version)
                    job_results.save()

                    data["results"] = job_results.get_public()
                    res = {
                        "status": SUCCESS,
                        "code": drf_status.HTTP_201_CREATED,
                        "error": "",
                        "data": data
                    }
            # end of checking it started

        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} create res={}")
                 .format(self.class_name,
                         json.dumps(res)[0:32]))

        return res
    # end of create

    def update(self,
               request,
               pk=None):
        """update

        Update an MLJob

        :param request: http request
        :param pk: MLJob.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} update pk={}")
                     .format(self.class_name,
                             pk))

            res = {
                "status": SUCCESS,
                "code": drf_status.HTTP_200_OK,
                "error": "not implemented yet",
                "data": data
            }
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} update res={}")
                 .format(self.class_name,
                         res))

        return res
    # end of update

    def get(self,
            request,
            pk):
        """get

        Get MLJob or Get Recent ML Jobs for User (if pk=None)

        :param request: http request
        :param pk: MLJob.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} get user_id={} pk={}")
                     .format(self.class_name,
                             request.user.id,
                             pk))

            db_query = (Q(user=request.user.id) & Q(id=pk))
            qset = []
            if pk:
                qset = MLJob.objects.select_related() \
                            .filter(db_query)
            else:
                db_query = (Q(user=request.user.id))
                qset = MLJob.objects.select_related() \
                            .filter(db_query) \
                            .order_by("-created") \
                            .all()[:settings.MAX_RECS_ML_JOB]

            if len(qset) == 1:
                data = qset[0].get_public()
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""
            elif len(qset) > 1:
                data["jobs"] = []
                for i in qset:
                    data["jobs"].append(i.get_public())
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""
            else:
                data = {}
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""

            res["status"] = SUCCESS
            res["data"] = data
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} get res={}")
                 .format(self.class_name,
                         json.dumps(res)[0:32]))

        return res
    # end of get

    def delete(self,
               request,
               pk):
        """delete

        Delete an MLJob

        :param request: http request
        :param pk: MLJob.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} delete pk={}")
                     .format(self.class_name,
                             pk))

            res = {
                "status": SUCCESS,
                "code": drf_status.HTTP_200_OK,
                "error": "not implemented yet",
                "data": data
            }
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": "not run",
                "data": last_step
            }
        # end of try/ex

        log.info(("{} delete res={}")
                 .format(self.class_name,
                         res))

        return res
    # end of delete

# end of MLJobsSerializer


class MLJobResultsSerializer(serializers.Serializer):

    user = UserSerializer(
                many=False)
    job = MLJobsSerializer(
                many=False,
                required=True)
    status = serializers.CharField(
                max_length=20,
                allow_blank=True,
                required=False,
                allow_null=True,
                default="initial")
    acc_data = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    error_data = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=False,
                trim_whitespace=True)
    version = serializers.IntegerField(
                default=1,
                required=False)

    request = None
    class_name = "MLJobResults"

    class Meta:
        fields = (
            "id",
            "user",
            "job",
            "status",
            "acc_data",
            "error_data",
            "version",
        )

    def create(self,
               request,
               validated_data):
        """create

        Create new MLJobResult

        :param request: http request
        :param validated_data: post dictionary
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} create data={}")
                     .format(self.class_name,
                             validated_data))

            res = {
                "status": SUCCESS,
                "code": drf_status.HTTP_200_OK,
                "error": "not implemented yet",
                "data": data
            }
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} create res={}")
                 .format(self.class_name,
                         res))

        return res
    # end of create

    def update(self,
               request,
               pk=None):
        """update

        Update an MLJobResult

        :param request: http request
        :param pk: MLJobResult.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} update pk={}")
                     .format(self.class_name,
                             pk))

            res = {
                "status": SUCCESS,
                "code": drf_status.HTTP_200_OK,
                "error": "not implemented yet",
                "data": data
            }
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} update res={}")
                 .format(self.class_name,
                         res))

        return res
    # end of update

    def get(self,
            request,
            pk):
        """get

        Start a new MLJobResult

        :param request: http request
        :param pk: MLJobResult.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} get user_id={} pk={}")
                     .format(self.class_name,
                             request.user.id,
                             pk))

            db_query = (Q(user=request.user.id) & Q(id=pk))
            qset = []
            if pk:
                qset = MLJobResult.objects.select_related() \
                            .filter(db_query)
            else:
                db_query = (Q(user=request.user.id))
                qset = MLJobResult.objects.select_related().filter(
                        db_query).order_by(
                        "-created").all()[:settings.MAX_RECS_ML_JOB_RESULT]

            if len(qset) == 1:
                data = qset[0].get_public()
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""
            elif len(qset) > 1:
                data["results"] = []
                for i in qset:
                    data["results"].append(i.get_public(
                        include_model=settings.INCLUDE_ML_MODEL,
                        include_weights=settings.INCLUDE_ML_WEIGHTS))
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""
            else:
                data = {}
                res["code"] = drf_status.HTTP_200_OK
                res["error"] = ""

            res["status"] = SUCCESS
            res["data"] = data
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} get res={}")
                 .format(self.class_name,
                         json.dumps(res)[0:32]))

        return res
    # end of get

    def delete(self,
               request,
               pk):
        """delete

        Delete an MLJobResult

        :param request: http request
        :param pk: MLJobResult.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} delete pk={}")
                     .format(self.class_name,
                             pk))

            res = {
                "status": SUCCESS,
                "code": drf_status.HTTP_200_OK,
                "error": "not implemented yet",
                "data": data
            }
        except Exception as e:
            last_step = ("{} Failed with ex={}").format(
                            self.class_name,
                            e)
            log.error(last_step)
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": last_step,
                "data": last_step
            }
        # end of try/ex

        log.info(("{} delete res={}")
                 .format(self.class_name,
                         res))

        return res
    # end of delete

# end of MLJobResultsSerializer
