from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery_loaders.log.setup_logging import build_colorized_logger
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q


User = get_user_model()  # noqa

name = "user_tasks"
log = build_colorized_logger(name=name)


@shared_task
def task_get_user(
        user_data):
    """task_get_user

    :param user_data: user dictionary for lookup values
    """

    ret_data = {}

    label = "task_get_user"

    log.info(("task - {} - start "
              "user_data={}")
             .format(label,
                     user_data))

    user_id = user_data.get("user_id", None)
    if user_id:
        db_query = (Q(id=user_id))
        log.info(("finding user={}")
                 .format(
                    user_id))
        qset = User.objects.select_related().filter(db_query)
        if len(qset) == 0:
            log.error(("failed to find user={}")
                      .format(
                          user_id))
        else:
            obj = qset[0]
            log.info(("found user.id={} name={}")
                     .format(
                         obj.id,
                         obj.username))
            ret_data = {
                "id": obj.id,
                "username": obj.username,
                "email": obj.email
            }
    else:
        log.info(("no user_id in data={}")
                 .format(
                     user_data))
    # end of if user_id found

    log.info(("task - {} - done")
             .format(label))

    return ret_data
# end of task_get_user
