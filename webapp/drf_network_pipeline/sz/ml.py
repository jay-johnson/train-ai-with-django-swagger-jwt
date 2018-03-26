from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from rest_framework import serializers
from rest_framework import status as drf_status
from antinex_utils.log.setup_logging import build_colorized_logger
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
from drf_network_pipeline.pipeline.tasks import task_ml_job
from drf_network_pipeline.pipeline.tasks import \
    task_ml_process_worker_results
from drf_network_pipeline.pipeline.create_ml_prepare_record import \
    create_ml_prepare_record
from drf_network_pipeline.pipeline.create_ml_job_record import \
    create_ml_job_record


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
                allow_blank=True,
                trim_whitespace=True)
    meta_data = serializers.CharField(
                max_length=None,
                min_length=None,
                allow_blank=True,
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
                        str(job_res)[0:30]))

            # in sync mode the data is in the task
            # response object, so send it back
            # because the client is blocking on it
            if job_res["status"] == SUCCESS:
                res = {
                    "status": SUCCESS,
                    "code": drf_status.HTTP_201_CREATED,
                    "error": "",
                    "data": job_res["data"]
                }
            # if celery (full stack async mode)
            # is working on this task,
            # return the initial record data we have.
            # from there the client will have to poll
            # to get the final results
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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                required=False)
    meta_file = serializers.CharField(
                max_length=1024,
                allow_blank=False,
                required=False)
    ds_name = serializers.CharField(
                max_length=1024,
                allow_blank=False,
                required=False)
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

            # if the Full Stack is running with Celery
            # then it is assumed the task will be published
            # to the worker and only the MLJob and MLJobResult
            # records will be returned for polling the status
            # of the long-running training job
            task_name = "ml_job"
            get_result = True
            ml_job_task = task_ml_job
            if settings.CELERY_ENABLED:
                ml_job_task = task_ml_job.delay
                get_result = False

            req_data = validated_data
            req_data["user_id"] = user_id

            create_res = create_ml_job_record(
                            req_data=req_data)
            user_obj = create_res.get(
                "user_obj",
                None)
            ml_job_obj = create_res.get(
                "ml_job_obj",
                None)
            ml_result_obj = create_res.get(
                "ml_result_obj",
                None)
            if not user_obj:
                res["error"] = ("{} - Failed to find User").format(
                                    task_name)
                res["status"] = ERR
                res["code"] = drf_status.HTTP_400_BAD_REQUEST
                res["error"] = create_res.get("err", "error not set")
                res["data"] = None
                log.error(res["error"])
                return res
            if not ml_job_obj:
                res["error"] = ("{} - Failed to create MLJob").format(
                                    task_name)
                res["status"] = ERR
                res["code"] = drf_status.HTTP_400_BAD_REQUEST
                res["error"] = create_res.get("err", "error not set")
                res["data"] = None
                log.error(res["error"])
                return res
            if not ml_result_obj:
                res["error"] = ("{} - Failed to create MLJobResult").format(
                                    task_name)
                res["status"] = ERR
                res["code"] = drf_status.HTTP_400_BAD_REQUEST
                res["error"] = create_res.get("err", "error not set")
                res["data"] = None
                log.error(res["error"])
                return res

            req_data["user_data"] = {
                "id": user_obj.id,
                "email": user_obj.email,
                "username": user_obj.username
            }
            req_data["ml_job_data"] = ml_job_obj.get_public()
            req_data["ml_result_data"] = ml_result_obj.get_public()

            job_res = run_task(
                task_method=ml_job_task,
                task_name=task_name,
                req_data=req_data,
                get_result=get_result)

            log.info(("task={} res={}")
                     .format(
                        task_name,
                        str(job_res)[0:30]))

            # in sync mode the data is in the task
            # response object, so send it back
            # because the client is blocking on it
            if job_res["status"] == SUCCESS:
                res = {
                    "status": SUCCESS,
                    "code": drf_status.HTTP_201_CREATED,
                    "error": "",
                    "data": {
                        "job": job_res["data"]["job"],
                        "results": job_res["data"]["results"]
                    }
                }
            # if celery (full stack async mode)
            # is working on this task,
            # return the initial record data we have.
            # from there the client will have to poll
            # to get the final results
            elif not get_result and job_res["status"] == NOTDONE:
                res = {
                    "status": SUCCESS,
                    "code": drf_status.HTTP_201_CREATED,
                    "error": "",
                    "data": {
                        "job": req_data["ml_job_data"],
                        "results": req_data["ml_result_data"]
                    }
                }
            else:
                res = {
                    "status": ERR,
                    "code": drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": job_res["err"],
                    "data": {
                        "job": None,
                        "results": None
                    }
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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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

            if settings.ANTINEX_WORKER_ENABLED:
                if settings.CELERY_ENABLED:
                    task_ml_process_worker_results.delay()
                else:
                    task_ml_process_worker_results()
            # end of processing results from the worker if any

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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

            if settings.ANTINEX_WORKER_ENABLED:
                if settings.CELERY_ENABLED:
                    task_ml_process_worker_results.delay()
                else:
                    task_ml_process_worker_results()
            # end of processing results from the worker if any

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

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
                 .format(
                    self.class_name,
                    str(res)[0:30]))

        return res
    # end of delete

# end of MLJobResultsSerializer
