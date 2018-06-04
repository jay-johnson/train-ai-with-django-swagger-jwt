from rest_framework import viewsets
from rest_framework import permissions
from antinex_utils.log.setup_logging import build_colorized_logger
from rest_framework.response import Response
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLJobResult
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.sz.ml import MLPrepareSerializer
from drf_network_pipeline.sz.ml import MLJobsSerializer
from drf_network_pipeline.sz.ml import MLJobResultsSerializer


name = "ml"
log = build_colorized_logger(name=name)


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

    list:
        Return recent Prepared datasets

    create:
        Create new Prepared dataset of CSVs for analysis with /ml/run
        ---

        Here is a sample Prepare dataset
        ```
        {
            "title": "Prepare new Dataset from recordings",
            "desc": "",
            "ds_name": "new_recording",
            "full_file": "/tmp/fulldata_attack_scans.csv",
            "clean_file": "/tmp/cleaned_attack_scans.csv",
            "meta_suffix": "metadata.json",
            "output_dir": "/tmp/",
            "ds_dir": "/opt/antinex/datasets",
            "ds_glob_path": "/opt/antinex/datasets/*/*.csv",
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
                    validated_data=request.data,
                    pk=pk)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of update

    def retrieve(self,
                 request,
                 pk):
        log.info(("{} get")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of retrieve

    def list(self,
             request):
        log.info(("{} list")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=None)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of list

    def destroy(self,
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

    list:
        Return recent ML Jobs

    create:
        Create a new ML Job
        ---

        Here is a sample Job

        Please fix the datasets entry below:

        ```
        {
            "label": "Full-Django-AntiNex-Simple-Scaler-DNN",
            "ml_type": "classification",
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
            "version": 1,
            "dataset": "/opt/antinex/antinex-datasets/v1/
            webapps/django/training-ready/v1_django_cleaned.csv"
        }
        ```
        Please fix the datasets entry ^ before trying
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
                    validated_data=request.data,
                    pk=pk)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of update

    def retrieve(self,
                 request,
                 pk):
        log.info(("{} get")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of retrieve

    def list(self,
             request):
        log.info(("{} list")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=None)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of list

    def destroy(self,
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

    list:
        Return recent ML Job Results

    create:
        Create a new ML Job Result

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
                    validated_data=request.data,
                    pk=pk)

        return Response(obj_res["data"],
                        obj_res["code"])
    # end of update

    def retrieve(self,
                 request,
                 pk):
        log.info(("{} get")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=pk)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of retrieve

    def list(self,
             request):
        log.info(("{} list")
                 .format(self.name))
        obj_res = self.serializer_class().get(
                    request=request,
                    pk=None)
        return Response(obj_res["data"],
                        obj_res["code"])
    # end of list

    def destroy(self,
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
