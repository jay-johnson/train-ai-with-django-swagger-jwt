import logging
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from network_pipeline.log.setup_logging import setup_logging


setup_logging()
name = "user-sz"
log = logging.getLogger(name)


User = get_user_model()  # noqa


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=32,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        min_length=4,
        write_only=True
    )

    class Meta:
        model = User
        fields = ("url",
                  "username",
                  "password",
                  "email")

    def create(self, validated_data):
        """create

        :param validated_data: post dict
        """

        log.info(("creating user={} email={}")
                 .format(validated_data["username"],
                         validated_data["email"]))

        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"]
        )
        user.set_password(validated_data["password"])
        user.save()

        log.info(("created id={} user={} email={}")
                 .format(user.id,
                         user.username,
                         user.email))

        return user
    # end of create

# end of UserSerializer
