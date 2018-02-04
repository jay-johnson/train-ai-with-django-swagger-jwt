import logging
from rest_framework import viewsets
from rest_framework import permissions
from network_pipeline.log.setup_logging import setup_logging
from rest_framework.response import Response
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLJobResult
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.sz.ml import MLPrepareSerializer
from drf_network_pipeline.sz.ml import MLJobsSerializer
from drf_network_pipeline.sz.ml import MLJobResultsSerializer


setup_logging()
name = "ml"
log = logging.getLogger(name)


class MLPrepareViewSet(
        # mixins.CreateModelMixin,
        # mixins.RetrieveModelMixin,
        # mixins.UpdateModelMixin,
        # mixins.DestroyModelMixin,
        # mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    retrieve:
        Return a Prepared dataset

    create:
        Create new Prepared dataset of CSVs for analysis with /ml/run
        ---

        Here is a sample Prepare dataset
        ```
        {
            "csv_file": "/tmp/cleaned_attack_scans.csv",
            "meta_file": "/tmp/cleaned_metadata.json",
            "title": "Keras DNN 1.0.9",
            "desc": "Tensorflow backend with simulated data",
            "ds_name": "cleaned",
            "algo_name": "dnn",
            "ml_type": "keras",
            "predict_feature": "label_value",
            "training_data": "{}",
            "pre_proc": "{}",
            "post_proc": "{}",
            "meta_data": "{}",
            "version": 0
        }
        ```
    delete:
        Remove an existing Prepared dataset

    update:
        Update a Prepared dataset
    """

    # A viewset that provides the standard actions
    name = "ml_prep"
    model = MLPrepare
    queryset = MLPrepare.objects.all()
    serializer_class = MLPrepareSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'GET':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'PUT':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(),)
    # end of get_permissions

    def create(self,
               request):
        log.info(("{} create")
                 .format(self.name))
        obj_res = self.serializer_class().create(
                    request=request,
                    validated_data=request.data)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of create

    def update(self,
               request,
               pk=None):
        log.info(("{} update")
                 .format(self.name))
        obj_res = self.serializer_class().update(
                    request=request,
                    pk=pk)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of update

    def get(self,
            request,
            pk):
        log.info(("{} get")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of get

    def delete(self,
               request,
               pk=None):
        log.info(("{} delete")
                 .format(self.name))
        obj_res = self.serializer_class().delete(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of delete

# end of MLPrepareViewSet


class MLJobViewSet(
        # mixins.CreateModelMixin,
        # mixins.RetrieveModelMixin,
        # mixins.UpdateModelMixin,
        # mixins.DestroyModelMixin,
        # mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    retrieve:
        Return a ML Job instance

    create:
        Create a new ML Job
        ---

        Here is a sample Job
        ```
        {
            "csv_file": "/tmp/cleaned_attack_scans.csv",
            "meta_file": "/tmp/cleaned_metadata.json",
            "title": "Keras DNN 1.0.9",
            "desc": "Tensorflow backend with simulated data",
            "ds_name": "cleaned",
            "algo_name": "dnn",
            "ml_type": "keras",
            "predict_feature": "label_value",
            "training_data": "{}",
            "pre_proc": "{}",
            "post_proc": "{}",
            "meta_data": "{}",
            "version": 0
        }
        ```
    delete:
        Remove an existing ML Job

    update:
        Update a ML Job
    """

    # A viewset that provides the standard actions
    name = "ml_job"
    model = MLJob
    queryset = MLJob.objects.all()
    serializer_class = MLJobsSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'GET':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'PUT':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(),)
    # end of get_permissions

    def create(self,
               request):
        log.info(("{} create")
                 .format(self.name))
        obj_res = self.serializer_class().create(
                    request=request,
                    validated_data=request.data)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of create

    def update(self,
               request,
               pk=None):
        log.info(("{} update")
                 .format(self.name))
        obj_res = self.serializer_class().update(
                    request=request,
                    pk=pk)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of update

    def get(self,
            request,
            pk):
        log.info(("{} get")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of get

    def delete(self,
               request,
               pk=None):
        log.info(("{} delete")
                 .format(self.name))
        obj_res = self.serializer_class().delete(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of delete

# end of MLJobViewSet


class MLJobResultViewSet(
        # mixins.CreateModelMixin,
        # mixins.RetrieveModelMixin,
        # mixins.UpdateModelMixin,
        # mixins.DestroyModelMixin,
        # mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    retrieve:
        Return a ML Job Result.

    create:
        Create a new ML Job Result
        ---

        Here is a sample Job Result:
        ```
        {}
        ```
    delete:
        Remove an existing ML Job Result

    update:
        Update a ML Job Result
    """

    # A viewset that provides the standard actions
    name = "mljob_result"
    model = MLJobResult
    queryset = MLJobResult.objects.all()
    serializer_class = MLJobResultsSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'GET':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'PUT':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(),)
    # end of get_permissions

    def create(self,
               request):
        log.info(("{} create")
                 .format(self.name))
        obj_res = self.serializer_class().create(
                    request=request,
                    validated_data=request.data)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of create

    def update(self,
               request,
               pk=None):
        log.info(("{} update")
                 .format(self.name))
        obj_res = self.serializer_class().update(
                    request=request,
                    pk=pk)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of update

    def get(self,
            request,
            pk):
        log.info(("{} get")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of get

    def delete(self,
               request,
               pk=None):
        log.info(("{} delete")
                 .format(self.name))
        obj_res = self.serializer_class().delete(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of delete

# end of MLJobResultViewSet