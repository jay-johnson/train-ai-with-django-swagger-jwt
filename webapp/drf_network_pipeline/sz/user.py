import json
from rest_framework.validators import UniqueValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.validators import validate_email
from rest_framework import serializers
from rest_framework import status as drf_status
from celery_loaders.log.setup_logging import build_colorized_logger
from drf_network_pipeline.pipeline.consts import SUCCESS
from drf_network_pipeline.pipeline.consts import FAILED
from drf_network_pipeline.pipeline.consts import ERR
from drf_network_pipeline.job_utils.run_task import run_task
from drf_network_pipeline.users.tasks import task_get_user


name = "user-sz"
log = build_colorized_logger(name=name)


User = get_user_model()  # noqa


# Serializers define the API representation.
class UserSerializer(serializers.Serializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=64,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        min_length=4,
        write_only=True
    )
    first_name = serializers.CharField(
        max_length=30,
        required=False,
        validators=[]
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        validators=[]
    )

    request = None
    class_name = "user_sz"

    class Meta:
        model = User
        fields = ("url",
                  "id",
                  "username",
                  "password",
                  "first_name",
                  "last_name",
                  "email")

    def lookup_user(
            self,
            user_id):
        """lookup_user

        :param user_id: user id
        """

        lookup_user_data = {
            "user_id": user_id
        }

        # if Celery is enabled use it
        task_method = task_get_user
        if settings.CELERY_ENABLED:
            task_method = task_get_user.delay

        task_name = "get_user"
        user_res = run_task(
            task_method=task_method,
            task_name=task_name,
            req_data=lookup_user_data,
            get_result=True)

        return user_res

    # end of lookup_user

    def create(self,
               request,
               validated_data):
        """create

        :param validated_data: post dict
        """

        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": None
        }

        log.info(("creating user={} email={}")
                 .format(validated_data["username"],
                         validated_data["email"]))

        email = validated_data.get("email", None)
        username = validated_data.get("username", None)
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")
        password = validated_data.get("password", "")
        if not email:
            res = {
                "status": FAILED,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": "missing email address",
                "data": "missing email address"
            }
            log.info(res["error"])
            return res
        if not username:
            res = {
                "status": FAILED,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": "missing username",
                "data": "missing username"
            }
            log.info(res["error"])
            return res
        else:
            if len(username) > 30:
                res = {
                    "status": FAILED,
                    "code": drf_status.HTTP_400_BAD_REQUEST,
                    "error": "username too long",
                    "data": "username too long"
                }
                log.info(res["error"])
                return res
        # check usernames

        if not password:
            res = {
                "status": FAILED,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": "missing password",
                "data": "missing password"
            }
            log.info(res["error"])
            return res
        if len(str(password)) < 4:
            res = {
                "status": FAILED,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": "password too short",
                "data": "password too short"
            }
            log.info(res["error"])
            return res
        # end of password checks

        if User.objects.filter(username=username).exists():
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": ("username '{}' is already in use").format(
                            username)
            }
            res["data"] = res["error"]
            log.info(res["error"])
            return res
        # end of checking for unique email
        if User.objects.filter(email=email).exists():
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": ("email '{}' is already in use").format(
                            email)
            }
            res["data"] = res["error"]
            log.info(res["error"])
            return res
        # end of checking for unique email
        try:
            validate_email(email)
        except Exception as f:
            log.info(("invalid email: '{}'")
                     .format(
                        email))
            res = {
                "status": ERR,
                "code": drf_status.HTTP_400_BAD_REQUEST,
                "error": ("Please enter a valid email").format(
                            email)
            }
            res["data"] = res["error"]
            return res
        # end of validating email

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()

        log.info(("created id={} user={} email={}")
                 .format(
                    user.id,
                    user.username,
                    user.email))

        user_res = self.lookup_user(
                        user.id)

        if user_res["status"] == SUCCESS:
            res["code"] = drf_status.HTTP_201_CREATED
            res["status"] = SUCCESS
            res["data"] = user_res["data"]
            log.info(("celery={} - found user={}")
                     .format(
                        settings.CELERY_ENABLED,
                        res["data"]))
        else:
            log.error(("celery={} - get "
                       "user={} status={} err={}")
                      .format(
                        settings.CELERY_ENABLED,
                        user.id,
                        user_res["status"],
                        user_res["err"]))
            res["error"] = ("user_id={} not found").format(
                                user.id)
            res["code"] = drf_status.HTTP_400_BAD_REQUEST
            res["status"] = SUCCESS
            res["data"] = None
        # end of looking up user

        return res
    # end of create

    def get(self,
            request,
            pk):
        """get

        Get user

        :param request: http request
        :param pk: User.id
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
                     .format(
                        self.class_name,
                        request.user.id,
                        pk))

            user_id = request.user.id

            user_res = self.lookup_user(
                            user_id)

            if user_res["status"] == SUCCESS:
                res["code"] = drf_status.HTTP_200_OK
                res["status"] = SUCCESS
                res["data"] = user_res["data"]
                log.info(("celery={} - found user={}")
                         .format(
                            settings.CELERY_ENABLED,
                            res["data"]))
            else:
                log.error(("celery={} - get "
                           "user={} status={} err={}")
                          .format(
                            settings.CELERY_ENABLED,
                            user_id,
                            user_res["status"],
                            user_res["err"]))
                res["error"] = ("user_id={} not found").format(
                                    user_id)
                res["code"] = drf_status.HTTP_400_BAD_REQUEST
                res["status"] = SUCCESS
                res["data"] = None
            # end of looking up user

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

    def update(self,
               request,
               validated_data,
               pk=None):
        """update

        Update User

        :param request: http request
        :param validated_data: dict of values
        :param pk: User.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} update id={}")
                     .format(self.class_name,
                             request.user.id))

            user_id = request.user.id
            user_obj = User.objects.filter(Q(id=user_id)).first()

            if user_obj:
                new_username = validated_data.get("username", None)
                new_email = validated_data.get("email", None)
                new_password = validated_data.get("password", None)
                new_first = validated_data.get("first_name", None)
                new_last = validated_data.get("last_name", None)

                if new_username and user_obj.username != new_username:
                    if User.objects.filter(username=new_username).exists():
                        res = {
                            "status": ERR,
                            "code": drf_status.HTTP_400_BAD_REQUEST,
                            "error": ("username '{}' is already "
                                      "in use").format(
                                        new_username)
                        }
                        res["data"] = res["error"]
                        return res
                    else:
                        user_obj.username = new_username
                # end of checking for unique email
                if new_email and user_obj.email != new_email:
                    if User.objects.filter(email=new_email).exists():
                        res = {
                            "status": ERR,
                            "code": drf_status.HTTP_400_BAD_REQUEST,
                            "error": ("email '{}' is already in use").format(
                                        new_email)
                        }
                        res["data"] = res["error"]
                        return res
                    # end of checking for unique email
                    try:
                        validate_email(new_email)
                        user_obj.email = new_email
                    except Exception as f:
                        log.info(("user.id tried invalid email={}")
                                 .format(
                                     user_obj.id,
                                     new_email))
                        res = {
                            "status": ERR,
                            "code": drf_status.HTTP_400_BAD_REQUEST,
                            "error": ("'{}' is not a valid email").format(
                                        new_email)
                        }
                        res["data"] = res["error"]
                        return res
                # end of setting email

                if new_first and user_obj.first_name != new_first:
                    user_obj.first_name = new_first
                if new_last and user_obj.last_name != new_last:
                    user_obj.last_name = new_last
                if new_password:
                    user_obj.set_password(new_password)
                log.info(("saving user.id={} "
                          "username={} email={}")
                         .format(
                            user_obj.id,
                            user_obj.username,
                            user_obj.first_name,
                            user_obj.last_name))
                user_obj.save()
                log.info("getting updated user")
                user_res = self.lookup_user(
                                user_obj.id)
                res["code"] = drf_status.HTTP_200_OK
                res["status"] = SUCCESS
                res["data"] = user_res["data"]
                log.info(("celery={} - updated user={}")
                         .format(
                            settings.CELERY_ENABLED,
                            res["data"]))
            else:
                res["error"] = ("failed to find user_id={}").format(
                                    user_id)
                res["code"] = drf_status.HTTP_400_BAD_REQUEST
                res["status"] = FAILED
                res["data"] = None
                log.info(res["error"])
            # end of updating user record

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

    def delete(self,
               request,
               pk):
        """delete

        Delete a User

        :param request: http request
        :param pk: User.id
        """

        data = {}
        res = {
            "status": FAILED,
            "code": drf_status.HTTP_400_BAD_REQUEST,
            "error": "not run",
            "data": data
        }

        try:
            log.info(("{} delete id={}")
                     .format(self.class_name,
                             request.user.id))

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

# end of UserSerializer
