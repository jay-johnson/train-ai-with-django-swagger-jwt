from celery_loaders.log.setup_logging import build_colorized_logger
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q
from drf_network_pipeline.pipeline.consts import SUCCESS
from drf_network_pipeline.pipeline.consts import FAILED
from drf_network_pipeline.pipeline.consts import NOTRUN


User = get_user_model()  # noqa

name = "user_tasks"
log = build_colorized_logger(name=name)


def db_lookup_user(
        user_id=None,
        use_cache=False):
    """db_lookup_user

    :param user_id: user id
    :param use_cache: cache data
    """

    res = {
        "status": NOTRUN,
        "err": "not-run",
        "data": None,
        "user_obj": None,
        "profile_obj": None
    }

    if not user_id:
        log.error(("db_lookup_user user_id={}")
                  .format(
                      user_id))
        return res
    # check user_id is there

    db_query = (Q(id=user_id))
    log.info(("finding user={} cache={}")
             .format(
                user_id,
                use_cache))
    qset = None

    if use_cache:
        qset = User.objects.select_related().filter(
                    db_query).cache()
    else:
        qset = User.objects.select_related().filter(
                    db_query)
    # end of if caching all records or not

    if len(qset) == 0:
        res["err"] = ("failed to find user={}").format(
                        user_id)
        log.error(res["err"])
        res["status"] = FAILED
        res["data"] = None
        res["obj"] = None
    else:
        obj = qset[0]
        log.info(("found user.id={} name={}")
                 .format(
                    obj.id,
                    obj.username))
        # remember to only send json-serializables back
        res["data"] = {
            "id": obj.id,
            "username": obj.username,
            "email": obj.email
        }
        res["user_obj"] = obj
        res["profile_obj"] = None
        res["status"] = SUCCESS
    # if the query worked

    return res
# end of db_lookup_user
