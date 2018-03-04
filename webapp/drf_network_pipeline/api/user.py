from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from drf_network_pipeline.sz.user import UserSerializer
from antinex_utils.log.setup_logging import build_colorized_logger


name = "user-api"
log = build_colorized_logger(name=name)


User = get_user_model()  # noqa


# ViewSets define the view behavior.
class UserViewSet(
        viewsets.GenericViewSet):

    """
    retrieve:
        Return a User

    list:
        Return Users

    create:
        Create new User

    delete:
        Remove a User

    update:
        Update a User
    """

    # A viewset that provides the standard actions
    name = "user_api"
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return (permissions.AllowAny(),)
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

# end of UserViewSet
