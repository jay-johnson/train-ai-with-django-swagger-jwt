import os
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import PROTECT
from antinex_utils.utils import convert_to_date

# with postgres use this for the JSONField type:
if os.environ.get("POSTGRES_DB", "") != "":  # noqa
    from django.contrib.postgres.fields import JSONField  # noqa
else:  # noqa
    from jsonfield import JSONField  # noqa
# end of if using postgres vs another db type for JSONField support


User = get_user_model()  # noqa


class MLPrepare(models.Model):

    STATUS = (
        ('requested', 'requested'),
        ('initial', 'initial'),
        ('running', 'running'),
        ('preproc', 'preproc'),
        ('postproc', 'postproc'),
        ('uploading', 'uploading'),
        ('archiving', 'archiving'),
        ('finished', 'finished'),
        ('notifying', 'notifying'),
        ('error', 'error'),
        ('failed', 'failed'),
        ('cancelled', 'cancelled'),
    )

    CONTROL_STATE = (
        ('active', 'active'),
        ('finished', 'finished'),
        ('pause', 'pause'),
        ('cancel', 'cancel'),
        ('delete', 'delete'),
        ('error', 'error'),
    )

    user = models.ForeignKey(
                User,
                on_delete=PROTECT,
                related_name='user_ml_prepare',
                db_index=True,
                null=False)
    status = models.CharField(
                choices=STATUS,
                max_length=20,
                default="initial")
    control_state = models.CharField(
                choices=CONTROL_STATE,
                max_length=20,
                default="active")
    title = models.CharField(
                max_length=256,
                null=True,
                default=None)
    desc = models.CharField(
                max_length=256,
                null=True,
                default=None)
    full_file = models.CharField(
                max_length=1024,
                null=False)
    clean_file = models.CharField(
                max_length=1024,
                null=False)
    meta_suffix = models.CharField(
                max_length=256,
                default="metadata.json")
    output_dir = models.CharField(
                max_length=1024,
                null=False)
    ds_dir = models.CharField(
                max_length=1024,
                null=False)
    ds_glob_path = models.CharField(
                max_length=1024,
                null=False)
    pipeline_files = JSONField(
                null=False)
    post_proc = JSONField(
                null=False)
    label_rules = JSONField(
                null=False)
    meta_data = JSONField(
                null=False)
    tracking_id = models.CharField(
                max_length=512)
    version = models.IntegerField(
                default=1)
    created = models.DateTimeField(
                auto_now_add=True)
    updated = models.DateTimeField(
                auto_now=True)
    deleted = models.DateTimeField(
                default=None,
                null=True)

    def get_public(self):
        node = {
            "id": self.id,
            "user_id": self.user.id,
            "user_name": self.user.username,
            "status": self.status,
            "control_state": self.control_state,
            "title": self.title,
            "desc": self.desc,
            "full_file": self.full_file,
            "clean_file": self.clean_file,
            "meta_suffix": self.meta_suffix,
            "output_dir": self.output_dir,
            "ds_dir": self.ds_dir,
            "ds_glob_path": self.ds_glob_path,
            "pipeline_files": self.pipeline_files,
            "post_proc": self.post_proc,
            "label_rules": self.label_rules,
            "tracking_id": self.tracking_id,
            "version": self.version,
            "created": convert_to_date(self.created),
            "updated": convert_to_date(self.updated),
            "deleted": convert_to_date(self.deleted)
        }
        return node
    # end of get_public

# end of MLPrepare


class MLJob(models.Model):

    ML_TYPES = (
        ('keras-ai-tf', 'keras-ai-tf'),
        ('mxnet-ai', 'mxnet-ai'),
        ('xgb-regressor', 'xgb-regressor'),
        ('xgb-classifier', 'xgb-classifier'),
    )

    STATUS = (
        ('requested', 'requested'),
        ('initial', 'initial'),
        ('training', 'training'),
        ('predicting', 'predicting'),
        ('analyzing', 'analyzing'),
        ('compiling', 'compiling'),
        ('evaluating', 'evaluating'),
        ('plotting', 'plotting'),
        ('uploading', 'uploading'),
        ('caching', 'caching'),
        ('waiting', 'waiting'),
        ('completed', 'completed'),
        ('setup', 'setup'),
        ('emailing', 'emailing'),
        ('pending', 'pending'),
        ('waiting', 'waiting'),
        ('started', 'started'),
        ('running', 'running'),
        ('postproc', 'postproc'),
        ('uploading', 'uploading'),
        ('archiving', 'archiving'),
        ('finished', 'finished'),
        ('notifying', 'notifying'),
        ('error', 'error'),
        ('failed', 'failed'),
        ('cancelled', 'cancelled'),
    )

    CONTROL_STATE = (
        ('active', 'active'),
        ('finished', 'finished'),
        ('pause', 'pause'),
        ('cancel', 'cancel'),
        ('delete', 'delete'),
        ('error', 'error'),
    )

    user = models.ForeignKey(
                User,
                on_delete=PROTECT,
                related_name='user_ml_job',
                db_index=True,
                null=False)
    title = models.CharField(
                max_length=512,
                null=True,
                default=None)
    desc = models.CharField(
                max_length=512,
                null=True,
                default=None)

    ds_name = models.CharField(
                max_length=512)
    algo_name = models.CharField(
                max_length=512)
    ml_type = models.CharField(
                choices=ML_TYPES,
                max_length=20)
    status = models.CharField(
                choices=STATUS,
                max_length=20,
                default="initial")
    control_state = models.CharField(
                choices=CONTROL_STATE,
                max_length=20,
                default="active")
    predict_feature = models.CharField(
                max_length=512)
    predict_manifest = JSONField(
                null=True,
                default=None)
    training_data = JSONField(
                null=True,
                default=None)
    pre_proc = JSONField(
                null=True,
                default=None)
    post_proc = JSONField(
                null=True,
                default=None)

    meta_data = JSONField(
                null=True,
                default=None)
    tracking_id = models.CharField(
                max_length=512)

    version = models.IntegerField(
                default=1)
    created = models.DateTimeField(
                auto_now_add=True)
    updated = models.DateTimeField(
                auto_now=True)
    deleted = models.DateTimeField(
                default=None,
                null=True)

    def get_public(self):
        node = {
            "id": self.id,
            "user_id": self.user.id,
            "user_name": self.user.username,
            "title": self.title,
            "desc": self.desc,
            "ds_name": self.ds_name,
            "algo_name": self.algo_name,
            "ml_type": self.ml_type,
            "status": self.status,
            "control_state": self.control_state,
            "predict_feature": self.predict_feature,
            "predict_manifest": self.predict_manifest,
            "training_data": self.training_data,
            "pre_proc": self.pre_proc,
            "post_proc": self.post_proc,
            "meta_data": self.meta_data,
            "tracking_id": self.tracking_id,
            "version": self.version,
            "created": convert_to_date(self.created),
            "updated": convert_to_date(self.updated),
            "deleted": convert_to_date(self.deleted)
        }
        return node
    # end of get_public

# end of MLJob


class MLJobResult(models.Model):

    STATUS = (
        ('initial', 'initial'),
        ('waiting', 'waiting'),
        ('processing', 'processing'),
        ('uploading', 'uploading'),
        ('pause', 'pause'),
        ('cancel', 'cancel'),
        ('delete', 'delete'),
        ('finished', 'finished'),
        ('error', 'error'),
        ('failed', 'failed'),
    )

    user = models.ForeignKey(
                User,
                on_delete=PROTECT,
                related_name='ml_job_results_user',
                db_index=True,
                null=True,
                default=None)
    job = models.ForeignKey(
                MLJob,
                on_delete=PROTECT,
                related_name='ml_job_results_job',
                db_index=True,
                null=True,
                default=None)
    status = models.CharField(
                choices=STATUS,
                max_length=20,
                default="initial")
    test_size = models.FloatField(
                default=0.2)
    csv_file = models.CharField(
                max_length=512,
                null=True,
                default=None)
    meta_file = models.CharField(
                max_length=512,
                null=True,
                default=None)
    acc_data = JSONField(
                null=True,
                default=None)
    error_data = JSONField(
                null=True,
                default=None)
    model_json = JSONField(
                null=True,
                default=None)
    model_weights = JSONField(
                null=True,
                default=None)
    model_weights_file = models.CharField(
                max_length=512,
                null=True,
                default=None)
    acc_image_file = models.CharField(
                max_length=256,
                null=True,
                default=None)
    predictions_json = JSONField(
                null=True,
                default=None)
    version = models.IntegerField(
                default=1)
    created = models.DateTimeField(
                auto_now_add=True)
    updated = models.DateTimeField(
                auto_now=True)
    deleted = models.DateTimeField(
                default=None,
                null=True)

    def get_public(self,
                   include_model=True,
                   include_weights=True):
        node = {
            "id": self.id,
            "user_id": self.user.id,
            "user_name": self.user.username,
            "job_id": None,
            "status": self.status,
            "test_size": self.test_size,
            "csv_file": self.csv_file,
            "meta_file": self.meta_file,
            "version": self.version,
            "acc_data": self.acc_data,
            "error_data": self.error_data,
            "model_json": None,
            "model_weights": None,
            "acc_image_file": self.acc_image_file,
            "predictions_json": self.predictions_json,
            "created": convert_to_date(self.created),
            "updated": convert_to_date(self.updated),
            "deleted": convert_to_date(self.deleted)
        }

        if self.job:
            node["job_id"] = self.job.id
        if include_model:
            node["model_json"] = self.model_json
        if include_weights:
            node["model_weights"] = self.model_weights

        return node
    # end of get_public

# end of MLJobResult
