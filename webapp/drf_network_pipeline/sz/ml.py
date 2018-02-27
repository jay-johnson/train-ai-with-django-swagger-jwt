import os
import uuid
import json
import pandas as pd
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from rest_framework import serializers
from rest_framework import status as drf_status
from network_pipeline.consts import VALID
from network_pipeline.build_training_request import build_training_request
from celery_loaders.log.setup_logging import build_colorized_logger
from drf_network_pipeline.pipeline.consts import SUCCESS
from drf_network_pipeline.pipeline.consts import FAILED
from drf_network_pipeline.pipeline.consts import ERR
from drf_network_pipeline.pipeline.consts import NOTDONE
from drf_network_pipeline.sz.user import UserSerializer
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.pipeline.models import MLJobResult
from drf_network_pipeline.job_utils.run_task import run_task
from drf_network_pipeline.pipeline.tasks import task_ml_prepare
from drf_network_pipeline.pipeline.create_ml_prepare_record import \
    create_ml_prepare_record
from keras.models import Sequential
from keras.layers import Dense
import matplotlib
matplotlib.use("Agg")  # noqa
import matplotlib.pyplot as plt  # noqa


name = "ml-sz"
log = build_colorized_logger(name=name)


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
    meta_suffix = serializers.CharField(
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
                required=False,
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
            "meta_suffix",
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

            # if the Full Stack is running with Celery
            # then it is assumed the task will be published
            # to the worker and only the MLPrepare record will be
            # returned for polling the status
            # of the long-running job
            prepare_task_name = "ml_prepare"
            get_result = True
            prepare_task = task_ml_prepare
            if settings.CELERY_ENABLED:
                prepare_task = task_ml_prepare.delay
                get_result = False

            req_data = validated_data
            req_data["user_id"] = user_id

            create_res = create_ml_prepare_record(
                            req_data=req_data)
            user_obj = create_res.get(
                "user_obj",
                None)
            ml_prepare_obj = create_res.get(
                "ml_prepare_obj",
                None)
            if not user_obj:
                res["error"] = ("{} - Failed to find User").format(
                                    prepare_task_name)
                res["status"] = ERR
                res["error"] = create_res.get("err", "error not set")
                res["data"] = None
                log.error(res["error"])
                return res
            if not ml_prepare_obj:
                res["error"] = ("{} - Failed to create MLPrepare").format(
                                    prepare_task_name)
                res["status"] = ERR
                res["error"] = create_res.get("err", "error not set")
                res["data"] = None
                log.error(res["error"])
                return res

            req_data["user_data"] = {
                "id": user_obj.id,
                "email": user_obj.email,
                "username": user_obj.username
            }
            req_data["ml_prepare_data"] = ml_prepare_obj.get_public()

            job_res = run_task(
                task_method=prepare_task,
                task_name=prepare_task_name,
                req_data=req_data,
                get_result=get_result)

            log.info(("task={} res={}")
                     .format(
                        prepare_task_name,
                        job_res))

            if job_res["status"] == SUCCESS:
                res = {
                    "status": SUCCESS,
                    "code": drf_status.HTTP_201_CREATED,
                    "error": "",
                    "data": job_res["data"]
                }
            elif not get_result and job_res["status"] == NOTDONE:
                res = {
                    "status": SUCCESS,
                    "code": drf_status.HTTP_201_CREATED,
                    "error": "",
                    "data": req_data["ml_prepare_data"]
                }
            else:
                res = {
                    "status": ERR,
                    "code": drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": job_res["err"],
                    "data": job_res["data"]
                }
            # end of processing result
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
               validated_data,
               pk=None):
        """update

        Update an MLPrepare

        :param request: http request
        :param validated_data: dict of values
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

        Get MLPrepare record

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
    image_file = serializers.CharField(
                max_length=256,
                allow_blank=True,
                required=False,
                allow_null=True)
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
            "image_file",
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
            ml_type = str(validated_data["ml_type"]).strip().lower()
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

            image_file = None
            if "image_file" in validated_data:
                image_file = validated_data["image_file"]
            # end of saving file naming

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

            job_results = None
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

                scores = None
                model = Sequential()
                histories = []

                if ml_type == "regression":
                    log.info(("creating Keras - regression - "
                              "sequential model ml_type={}")
                             .format(ml_type))

                    # create the model
                    model.add(Dense(8,
                                    input_dim=len(
                                        ml_req["features_to_process"]),
                                    kernel_initializer="normal",
                                    activation="relu"))
                    model.add(Dense(6,
                                    kernel_initializer="normal",
                                    activation="relu"))
                    model.add(Dense(1,
                                    kernel_initializer="normal",
                                    activation="sigmoid"))

                    loss = "mse"
                    metrics = [
                        "mse",
                        "mae",
                        "mape",
                        "cosine"
                    ]

                    histories = [
                        "mean_squared_error",
                        "mean_absolute_error",
                        "mean_absolute_percentage_error",
                        "cosine_proximity"
                    ]

                    last_step = ("compiling model "
                                 "loss={} metrics={}").format(
                                    loss,
                                    metrics)
                    log.info(last_step)

                    # compile the model
                    model.compile(
                            loss=loss,
                            optimizer="adam",
                            metrics=metrics)

                else:
                    log.info(("creating Keras - sequential model"
                              "ml_type={}")
                             .format(ml_type))

                    # create the model
                    model.add(Dense(8,
                                    input_dim=len(
                                        ml_req["features_to_process"]),
                                    kernel_initializer="uniform",
                                    activation="relu"))
                    model.add(Dense(6,
                                    kernel_initializer="uniform",
                                    activation="relu"))
                    model.add(Dense(1,
                                    kernel_initializer="uniform",
                                    activation="sigmoid"))

                    histories = [
                        "val_loss",
                        "val_acc",
                        "loss",
                        "acc"
                    ]

                    last_step = "compiling model"
                    log.info(last_step)

                    # compile the model
                    model.compile(
                            loss="binary_crossentropy",
                            optimizer="adam",
                            metrics=["accuracy"])

                # end of classification vs regression

                last_step = ("fitting model - "
                             "epochs={} batch={} "
                             "verbose={} - please wait").format(
                                epochs,
                                batch_size,
                                verbose)
                log.info(last_step)

                # fit the model
                history = model.fit(
                            ml_req["X_train"],
                            ml_req["Y_train"],
                            validation_data=(
                                ml_req["X_test"],
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
                    log.info(("building job={} results")
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

                    log.info(("saving job={} results")
                             .format(job.id))
                    job_results.save()

                    try:
                        if history and len(histories) > 0:
                            log.info(("plotting history={} "
                                      "histories={}")
                                     .format(
                                         history,
                                         histories))
                            should_save = False
                            for h in histories:
                                if h in history.history:
                                    log.info(("plotting={}")
                                             .format(h))
                                    plt.plot(
                                        history.history[h],
                                        label=h)
                                    should_save = True
                                else:
                                    log.error(("missing history={}")
                                              .format(h))
                            # for all histories

                            if should_save:
                                if not image_file:
                                    image_file = ("{}/accuracy_job_"
                                                  "{}_result_{}.png").format(
                                                settings.IMAGE_SAVE_DIR,
                                                job.id,
                                                job_results.id,
                                                str(uuid.uuid4()).replace(
                                                    "-", ""))
                                log.info(("saving plots as image={}")
                                         .format(image_file))
                                plt.legend(loc='best')
                                plt.savefig(image_file)
                                if not os.path.exists(image_file):
                                    log.error(("Failed saving image={}")
                                              .format(image_file))
                                else:
                                    job_results.acc_image_file = \
                                            image_file
                            # end of saving file

                        # end of if there are hsitories to plot
                    except Exception as e:
                        if job and job_results:
                            log.error(("Failed saving job={} "
                                       "image_file={} ex={}")
                                      .format(
                                        job.id,
                                        image_file,
                                        e))
                        else:
                            log.error(("Failed saving "
                                       "image_file={} ex={}")
                                      .format(
                                        image_file,
                                        e))
                    # end of try/ex

                    log.info(("updating job={} results={}")
                             .format(
                                job.id,
                                job_results.id))
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
               validated_data,
               pk=None):
        """update

        Update an MLJob

        :param request: http request
        :param validated_data: dict of values
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
               validated_data,
               pk=None):
        """update

        Update an MLJobResult

        :param request: http request
        :param validated_data: dict of values
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

        Get MLResult record

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
