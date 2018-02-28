import os
import uuid
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.test import APIRequestFactory
from rest_framework.test import CoreAPIClient
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt import utils as jwt_utils
from network_pipeline.utils import ppj
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLJobResult
from drf_network_pipeline.api.ml import MLPrepareViewSet
from drf_network_pipeline.api.ml import MLJobViewSet
from drf_network_pipeline.api.ml import MLJobResultViewSet


User = get_user_model()  # noqa


class MLJobTest(APITestCase):

    def setUp(self):
        """setUp"""

        self.training_data = {}
        self.pre_proc = {}
        self.post_proc = {}
        self.meta_data = {}

        self.test_username = "mltestuser"
        self.test_password = "mltestpassword123!@#sadf"

        self.test_user = User.objects.create_user(
                            self.test_username,
                            "mltest@example.com",
                            self.test_password)
        self.test_ml_job = MLJob(
                            user=self.test_user,
                            title="MLJob test",
                            desc="ML Job Desc",
                            ds_name="test dataset",
                            algo_name="test algo",
                            ml_type="keras-ai-tf",
                            status="initial",
                            control_state="active",
                            predict_feature="label_value",
                            training_data=self.training_data,
                            pre_proc=self.pre_proc,
                            post_proc=self.post_proc,
                            meta_data=self.meta_data,
                            tracking_id="job test",
                            version=1)

        self.client = CoreAPIClient()

        # URL for creating an account.
        self.factory = APIRequestFactory()
        self.auth_url = "/api-token-auth/"
        self.token = None
        self.ml_run_url = "/ml/"
        self.ml_get_url = "/ml/"
        self.ml_get_result_url = "/mlresults/"
        self.ml_prep_url = "/ml_prepare/"
        self.jwt_auth = None
    # end setUp

    def login_user(self):
        """login_user"""
        data = {
            "username": self.test_username,
            "password": self.test_password
        }

        """
        Ensure JWT login view using form POST works.
        """
        client = APIClient(enforce_csrf_checks=True)

        response = client.post(self.auth_url, data, format="json")
        decoded_payload = jwt_utils.jwt_decode_handler(response.data["token"])
        self.token = response.data["token"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded_payload["username"], self.test_username)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(not self.token)
        self.jwt_auth = "JWT {}".format(self.token)
    # end of login_user

    def check_dataset_files_exist(self, data):
        """check_dataset_files_exist

        :param data: request dictionary
        """
        if not os.path.exists(data["csv_file"]):
            cur_dir = os.getcwd()
            csv_file = ("{}/drf_network_pipeline/tests/datasets/"
                        "cleaned_attack_scans.csv").format(
                            cur_dir)
            data["csv_file"] = csv_file
        # end of checking csv file exists or use the test one
        if not os.path.exists(data["meta_file"]):
            cur_dir = os.getcwd()
            meta_file = ("{}/drf_network_pipeline/tests/datasets/"
                         "cleaned_attack_scans.meta").format(
                            cur_dir)
            data["meta_file"] = meta_file
        # end of checking metadata file exists or use the test one
        return data
    # end of check_dataset_files_exist

    def check_data_dir_and_files_exist(self, data):
        """check_data_dir_and_files_exist

        :param data: request dictionary
        """
        if not os.path.exists(data["ds_dir"]):
            cur_dir = os.getcwd()
            data["ds_dir"] = ("{}/drf_network_pipeline/tests/"
                              "prepare").format(cur_dir)
            data["ds_glob_path"] = ("{}/*/*.csv").format(
                              data["ds_dir"])

        return data
    # end of check_data_dir_and_files_exist

    def build_ml_prepare_dataset(self, ds_name="simple"):
        """build_ml_prepare_dataset

        :param ds_name: type of ML Prepare to run
        """
        post_proc = {
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
        }
        label_rules = {
            "set_if_above": 85,
            "labels": [
                "not_attack",
                "attack"
            ],
            "label_values": [0, 1]
        }
        meta_data = {}
        pipelines_files = {}
        data = {
                "title": "Prepare new Dataset from recordings",
                "desc": "",
                "ds_name": "new recording: {}".format(str(uuid.uuid4())),
                "full_file": "/tmp/fulldata_attack_scans.csv",
                "clean_file": "/tmp/cleaned_attack_scans.csv",
                "meta_suffix": "metadata.json",
                "output_dir": "/tmp/",
                "ds_dir": "./drf_network_pipeline/tests/prepare",
                "ds_glob_path": "./drf_network_pipeline/tests/prepare/*/*.csv",
                "pipeline_files": json.dumps(pipelines_files),
                "meta_data": json.dumps(meta_data),
                "post_proc": json.dumps(post_proc),
                "label_rules": json.dumps(label_rules),
                "version": 1
        }

        if os.getenv("TEST_DATA_DIR", "") != "":
            data_dir = os.getenv("TEST_DATA_DIR", "")
            data["ds_dir"] = data_dir
            data["ds_glob_path"] = "{}/*/*.csv".format(data_dir)

        data = self.check_data_dir_and_files_exist(data)

        return data
    # end of build_ml_prepare_dataset

    def build_ml_job_dataset(self, ds_name="simple"):
        """build_ml_job_dataset

        :param ds_name: type of ML Job to run
        """
        data = {
            "csv_file": "/tmp/cleaned_attack_scans.csv",
            "meta_file": "/tmp/cleaned_metadata.json",
            "title": "Keras DNN - network-pipeline - {}".format(
                str(uuid.uuid4())),
            "desc": "Tensorflow backend with simulated data",
            "ds_name": "cleaned",
            "algo_name": "dnn",
            "ml_type": "keras-ai-tf",
            "predict_feature": "label_value",
            "training_data": "{\"epochs\": 1}",
            "pre_proc": "{}",
            "post_proc": "{}",
            "meta_data": "{}",
            "version": 1
        }

        if ds_name == "smart":
            data["training_data"] = "{\"epochs\": 10}"

        data = self.check_dataset_files_exist(data)

        return data
    # end of build_ml_job_dataset

    def test_not_logged_in_blocked_ml_job_create(self):
        """
        Not Logged in Users cannot - Create an ML Job
        """
        data = self.build_ml_job_dataset()
        request = self.factory.post(self.ml_run_url,
                                    data,
                                    format="json")
        view = MLJobViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, 401)
    # end of test_not_logged_in_blocked_ml_job_create

    def test_create_ml_job(self):
        """
        Create an ML Job
        """

        data = self.build_ml_job_dataset()
        # validate jwt tokens work
        self.login_user()
        request = self.factory.post(
                    self.ml_run_url,
                    data,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(MLJob.objects.count(), 1)
        self.assertEqual(MLJobResult.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["job"]["user_name"], self.test_username)
        self.assertEqual(
            response.data["job"]["title"], data["title"])
        self.assertEqual(
            len(json.dumps(
                response.data["results"]["model_json"])) > 0,
            True)
        self.assertEqual(
            len(json.dumps(
                response.data["results"]["model_weights"])) > 0,
            True)
    # end of test_create_ml_job

    def test_get_ml_job(self):
        """
        Get ML Job works
        """

        data = self.build_ml_job_dataset()
        # validate jwt tokens work
        self.login_user()
        request = self.factory.post(
                    self.ml_run_url,
                    data,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(MLJob.objects.count(), 1)
        self.assertEqual(MLJobResult.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["job"]["user_name"], self.test_username)
        self.assertEqual(
            response.data["job"]["title"], data["title"])

        job_data = response.data["job"]
        job_tracking_id = job_data["tracking_id"]
        job_id = int(job_data["id"])

        request = self.factory.get(
                    self.ml_get_url,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobViewSet.as_view({"get": "retrieve"})
        get_response = view(request, pk=job_id)
        self.assertEqual(
            get_response.data["user_name"], self.test_username)
        self.assertEqual(
            get_response.data["title"], data["title"])
        self.assertEqual(
            get_response.data["tracking_id"], job_tracking_id)
    # end of test_get_ml_job

    def test_get_recent_ml_jobs(self):
        """
        Get Recent ML Jobs for User
        """

        data = self.build_ml_job_dataset()
        num_to_create = 30
        created_jobs = []
        for i in range(0, num_to_create):
            status = "finished"
            control_state = "finished"
            new_obj = MLJob(
                            user=self.test_user,
                            title=data["title"],
                            desc=data["desc"],
                            ds_name=data["ds_name"],
                            algo_name=data["algo_name"],
                            ml_type=data["ml_type"],
                            status=status,
                            control_state=control_state,
                            predict_feature="label_value",
                            training_data={},
                            pre_proc={},
                            post_proc={},
                            meta_data={},
                            tracking_id="id_{}".format(i),
                            version=data["version"])
            new_obj.save()
            created_jobs.append(new_obj)
        # end of creating jobs

        self.login_user()
        request = self.factory.get(
                    self.ml_get_url,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobViewSet.as_view({"get": "list"})
        get_response = view(request)
        self.assertContains(get_response, "jobs")
        self.assertEqual(
            len(get_response.data["jobs"]),
            settings.MAX_RECS_ML_JOB)
        for idx, response_node in enumerate(get_response.data["jobs"]):
            db_idx = (len(created_jobs) - idx) - 1
            db_node = created_jobs[db_idx]
            self.assertEqual(response_node["id"], db_node.id)
            self.assertEqual(
                response_node["tracking_id"], db_node.tracking_id)
    # end of test_get_recent_ml_jobs

    def test_get_ml_job_with_not_found_job_id(self):
        """
        Get ML Job returns 200 but empty data
        """

        # validate jwt tokens work
        self.login_user()

        job_id = 777

        request = self.factory.get(
                    self.ml_get_url,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobViewSet.as_view({"get": "retrieve"})
        get_response = view(request, pk=job_id)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data, {})
    # end of test_get_ml_job_with_not_found_job_id

    def test_get_ml_job_result(self):
        """
        Get ML Job Result works
        """

        data = self.build_ml_job_dataset()
        # validate jwt tokens work
        self.login_user()
        request = self.factory.post(
                    self.ml_run_url,
                    data,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(MLJob.objects.count(), 1)
        self.assertEqual(MLJobResult.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["job"]["user_name"], self.test_username)
        self.assertEqual(
            response.data["job"]["title"], data["title"])

        job_id = int(response.data["job"]["id"])
        result_data = response.data["results"]
        result_id = int(result_data["id"])
        error_data = result_data["error_data"]

        request = self.factory.get(
                    self.ml_get_result_url,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobResultViewSet.as_view({"get": "retrieve"})
        get_response = view(request, pk=result_id)
        print(ppj(get_response.data))
        self.assertEqual(
            get_response.data["user_name"], self.test_username)
        self.assertEqual(
            get_response.data["job_id"], job_id)
        self.assertEqual(
            get_response.data["id"], result_id)
        self.assertEqual(
            get_response.data["error_data"], error_data)
        self.assertContains(
            get_response, "model_json")
        self.assertContains(
            get_response, "model_weights")
        self.assertEqual(
            len(json.dumps(get_response.data["model_json"])) > 0,
            True)
        self.assertEqual(
            len(json.dumps(get_response.data["model_weights"])) > 0,
            True)
    # end of test_get_ml_job_result

    def test_get_recent_ml_job_results(self):
        """
        Get Recent ML Job Results for User
        """

        data = self.build_ml_job_dataset()
        num_to_create = 30
        created_jobs = []
        created_results = []
        for i in range(0, num_to_create):
            status = "finished"
            control_state = "finished"
            new_job = MLJob(
                            user=self.test_user,
                            title=data["title"],
                            desc=data["desc"],
                            ds_name=data["ds_name"],
                            algo_name=data["algo_name"],
                            ml_type=data["ml_type"],
                            status=status,
                            control_state=control_state,
                            predict_feature="label_value",
                            training_data={},
                            pre_proc={},
                            post_proc={},
                            meta_data={},
                            tracking_id="id_{}".format(i),
                            version=data["version"])
            new_job.save()
            acc_data = {
                "accuracy": float(new_job.id * 1.25)
            }
            error_data = None
            new_results = MLJobResult(
                            user=self.test_user,
                            job=new_job,
                            status=status,
                            acc_data=acc_data,
                            error_data=error_data,
                            version=data["version"])
            new_results.save()
            created_jobs.append(new_job)
            created_results.append(new_results)
        # end of creating jobs

        self.login_user()
        request = self.factory.get(
                    self.ml_get_url,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobResultViewSet.as_view({"get": "list"})
        get_response = view(request)
        self.assertContains(get_response, "results")
        self.assertEqual(
            len(get_response.data["results"]),
            settings.MAX_RECS_ML_JOB_RESULT)
        for idx, response_node in enumerate(get_response.data["results"]):
            db_idx = (len(created_results) - idx) - 1
            db_node = created_results[db_idx]
            self.assertEqual(response_node["id"], db_node.id)
            self.assertEqual(
                response_node["acc_data"], db_node.acc_data)
            self.assertEqual(
                response_node["error_data"], db_node.error_data)
    # end of test_get_recent_ml_job_results

    def test_get_ml_job_result_with_not_found_job_result_id(self):
        """
        Get ML Job Result returns 200 but empty data
        """

        # validate jwt tokens work
        self.login_user()

        job_result_id = 777

        request = self.factory.get(
                    self.ml_get_result_url,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLJobResultViewSet.as_view({"get": "retrieve"})
        get_response = view(request, pk=job_result_id)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data, {})
    # end of test_get_ml_job_result_with_not_found_job_result_id

    def test_create_ml_prepare(self):
        """
        Create an ML Prepare
        """

        data = self.build_ml_prepare_dataset()
        # validate jwt tokens work
        self.login_user()
        request = self.factory.post(
                    self.ml_prep_url,
                    data,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLPrepareViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(MLPrepare.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["user_name"], self.test_username)
        self.assertEqual(
            response.data["title"], data["title"])
        self.assertEqual(
            response.data["control_state"], "finished")
        self.assertEqual(
            response.data["status"], "finished")
        self.assertEqual(
            response.data["ds_dir"], data["ds_dir"])
        self.assertEqual(
            response.data["full_file"],
            ("{}fulldata_attack_scans.csv").format(
                 data["output_dir"]))
        self.assertEqual(
            response.data["clean_file"],
            ("{}cleaned_attack_scans.csv").format(
                data["output_dir"]))
        self.assertEqual(len(response.data["label_rules"]) > 0, True)
        self.assertEqual(
            len(response.data["post_proc"]["drop_columns"]) > 0, True)
        self.assertEqual(
            len(response.data["post_proc"]["features_to_process"]) > 0, True)
        self.assertEqual(
            len(response.data["post_proc"]["ignore_features"]) > 0, True)
        self.assertEqual(
            len(response.data["post_proc"]["feature_to_predict"]) > 0, True)
    # end of test_create_ml_prepare

    def test_get_ml_prepare(self):
        """
        Get ML Prepare works
        """

        data = self.build_ml_prepare_dataset()
        # validate jwt tokens work
        self.login_user()
        request = self.factory.post(
                    self.ml_prep_url,
                    data,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLPrepareViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(MLPrepare.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["user_name"], self.test_username)
        self.assertEqual(
            response.data["title"], data["title"])

        prepare_data = response.data
        prepare_tracking_id = prepare_data["tracking_id"]
        prepare_id = int(prepare_data["id"])

        request = self.factory.get(
                    self.ml_prep_url,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLPrepareViewSet.as_view({"get": "retrieve"})
        get_response = view(request, pk=prepare_id)
        self.assertEqual(
            get_response.data["user_name"], self.test_username)
        self.assertEqual(
            get_response.data["title"], data["title"])
        self.assertEqual(
            get_response.data["id"], prepare_id)
        self.assertEqual(
            get_response.data["tracking_id"], prepare_tracking_id)
        self.assertEqual(
            get_response.data["control_state"], "finished")
        self.assertEqual(
            get_response.data["status"], "finished")
        self.assertEqual(
            get_response.data["ds_dir"], data["ds_dir"])
        self.assertEqual(
            get_response.data["full_file"],
            ("{}fulldata_attack_scans.csv").format(
                 data["output_dir"]))
        self.assertEqual(
            get_response.data["clean_file"],
            ("{}cleaned_attack_scans.csv").format(
                data["output_dir"]))
        self.assertEqual(prepare_data["label_rules"],
                         get_response.data["label_rules"])
        self.assertEqual(prepare_data["post_proc"]["drop_columns"],
                         prepare_data["post_proc"]["drop_columns"])
        self.assertEqual(prepare_data["post_proc"]["features_to_process"],
                         prepare_data["post_proc"]["features_to_process"])
        self.assertEqual(prepare_data["post_proc"]["ignore_features"],
                         prepare_data["post_proc"]["ignore_features"])
        self.assertEqual(prepare_data["post_proc"]["feature_to_predict"],
                         prepare_data["post_proc"]["feature_to_predict"])
    # end of test_get_ml_prepare

    def test_get_recent_ml_prepares(self):
        """
        Get Recent ML Prepares for User
        """

        data = self.build_ml_prepare_dataset()
        num_to_create = 30
        created_jobs = []
        for i in range(0, num_to_create):
            status = "finished"
            control_state = "finished"
            new_obj = MLPrepare(
                            user=self.test_user,
                            status=status,
                            control_state=control_state,
                            title=data["title"],
                            desc=data["desc"],
                            full_file=data["full_file"],
                            clean_file=data["clean_file"],
                            meta_suffix=data["meta_suffix"],
                            output_dir=data["output_dir"],
                            ds_dir=data["ds_dir"],
                            ds_glob_path=data["ds_glob_path"],
                            pipeline_files=data["pipeline_files"],
                            post_proc=data["post_proc"],
                            label_rules=data["label_rules"],
                            meta_data=data["meta_data"],
                            tracking_id="id_{}".format(i),
                            version=data["version"])
            new_obj.save()
            created_jobs.append(new_obj)
        # end of creating jobs

        self.login_user()
        request = self.factory.get(
                    self.ml_prep_url,
                    HTTP_AUTHORIZATION=self.jwt_auth,
                    format="json")
        view = MLPrepareViewSet.as_view({"get": "list"})
        get_response = view(request)
        self.assertContains(get_response, "prepares")
        self.assertEqual(
            len(get_response.data["prepares"]),
            settings.MAX_RECS_ML_PREPARE)
        for idx, response_node in enumerate(get_response.data["prepares"]):
            db_idx = (len(created_jobs) - idx) - 1
            db_node = created_jobs[db_idx]
            self.assertEqual(response_node["id"], db_node.id)
            self.assertEqual(
                response_node["tracking_id"], db_node.tracking_id)
    # end of test_get_recent_ml_prepares

# end of MLJobTest
