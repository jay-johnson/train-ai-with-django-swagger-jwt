"""
Django settings for drf_network_pipeline project.

For more information on this file, see
https://docs.djangoproject.com/en/{{ docs_version }}/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/
"""
import os
import ssl
from configurations import Configuration
from configurations import values
from kombu import Exchange
from kombu import Queue


class Common(Configuration):

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = values.SecretValue()

    # SECURITY WARNING: do not run with debug turned on in production!
    DEBUG = values.BooleanValue(False)

    # for using HTTPS in swagger
    SECURE_PROXY_SSL_HEADER = (
        os.getenv(
            'HTTP_X_FORWARDED_PROTOCOL_KEY',
            'HTTP_X_FORWARDED_PROTOCOL').strip().upper(),
        'https')

    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "webapp",
        "dev.antinex",
        "api.antinex.com"
        "ark.antinex.com"
    ]

    # Application definition
    INSTALLED_APPS = [
        "django.contrib.sites",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "whitenoise.runserver_nostatic",
        "django.contrib.staticfiles",

        "rest_framework",
        "rest_framework_swagger",
        "rest_framework.authtoken",
        "rest_registration",
        "rest_framework_jwt",
        "django_extensions",
        "django_celery_results",
        "cacheops",
        "debug_toolbar",
        "drf_network_pipeline.users",
        "drf_network_pipeline.pipeline",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "drf_network_pipeline.urls"

    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [
                "drf_network_pipeline/templates",
                "drf_network_pipeline/docs/build/html",
                "drf_network_pipeline/docs/build/html/modules"
            ],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "drf_network_pipeline.wsgi.application"

    # Database
    # https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases  # noqa E501
    DATABASES = values.DatabaseURLValue(
        "sqlite:///{}".format(os.path.join(BASE_DIR, "db.sqlite3"))
    )

    if os.environ.get("POSTGRES_DB", "") != "":
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "NAME": os.environ.get("POSTGRES_DB", "webapp"),
                "USER": os.environ.get("POSTGRES_USER", "postgres"),
                "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
                "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
                "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            },
        }
        # end of loading postgres
    # end of using the postgres db

    # Password validation
    # https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#auth-password-validators # noqa
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa
        },
    ]

    SITE_ID = 1

    # Internationalization
    # https://docs.djangoproject.com/en/{{ docs_version }}/topics/i18n/
    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/{{ docs_version }}/howto/static-files/
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATICFILES_STORAGE = \
        "whitenoise.storage.CompressedManifestStaticFilesStorage"
    STATICFILES_DIRS = [
        os.path.join(
            BASE_DIR,
            "drf_network_pipeline/docs/build/html/_static")
    ]
    MEDIA_URL = "/media/"
    MEDIA_ROOT = "{}/media".format(
        BASE_DIR)

    AUTH_USER_MODEL = "users.User"

    # https://github.com/szopu/django-rest-registration#configuration
    REST_REGISTRATION = {
        "REGISTER_VERIFICATION_ENABLED": False,
        "RESET_PASSWORD_VERIFICATION_URL": "/reset-password/",
        "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
        "VERIFICATION_FROM_EMAIL": "no-reply@example.com",
    }

    # http://getblimp.github.io/django-rest-framework-jwt/
    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": (
            "rest_framework.permissions.AllowAny",
            "rest_framework.permissions.IsAuthenticated",
        ),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
            "rest_framework.authentication.TokenAuthentication",
            "rest_framework.authentication.BasicAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        ),
        "DEFAULT_RENDERER_CLASSES": (
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ),
    }

    # http://getblimp.github.io/django-rest-framework-jwt/
    """

    One of these is breaking the api-token-auth - 2018-02-02

    JWT_AUTH = {
        "JWT_ENCODE_HANDLER":
        "rest_framework_jwt.utils.jwt_encode_handler",
        "JWT_DECODE_HANDLER":
        "rest_framework_jwt.utils.jwt_decode_handler",
        "JWT_PAYLOAD_HANDLER":
        "rest_framework_jwt.utils.jwt_payload_handler",
        "JWT_PAYLOAD_GET_USER_ID_HANDLER":
        "rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler",
        "JWT_RESPONSE_PAYLOAD_HANDLER":
        "rest_framework_jwt.utils.jwt_response_payload_handler",
        "JWT_SECRET_KEY": SECRET_KEY,
        "JWT_GET_USER_SECRET_KEY": None,
        "JWT_PUBLIC_KEY": None,
        "JWT_PRIVATE_KEY": None,
        "JWT_ALGORITHM": "HS256",
        "JWT_VERIFY": True,
        "JWT_VERIFY_EXPIRATION": True,
        "JWT_LEEWAY": 0,
        "JWT_EXPIRATION_DELTA": datetime.timedelta(seconds=300),
        "JWT_AUDIENCE": None,
        "JWT_ISSUER": None,
        "JWT_ALLOW_REFRESH": False,
        "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(days=7),
        "JWT_AUTH_HEADER_PREFIX": "JWT",
        "JWT_AUTH_COOKIE": None,
    }
    """

    INCLUDE_ML_MODEL = True
    INCLUDE_ML_WEIGHTS = True
    MAX_RECS_ML_PREPARE = 20
    MAX_RECS_ML_JOB = 20
    MAX_RECS_ML_JOB_RESULT = 20

    # for saving images to the host
    # on vbox
    if os.path.exists("/media/sf_shared"):
        IMAGE_SAVE_DIR = "/media/sf_shared"
    else:
        IMAGE_SAVE_DIR = os.getenv(
            "IMAGE_SAVE_DIR",
            "/tmp")
    # end of image save path

    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
    REDIS_BROKER_DB = int(os.environ.get("REDIS_BROKER_DB", "9"))
    REDIS_RESULT_DB = int(os.environ.get("REDIS_RESULT_DB", "10"))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
    if REDIS_PASSWORD == "":
        REDIS_PASSWORD = None

    # Sensible settings for celery
    CELERY_ENABLED = bool(os.environ.get("CELERY_ENABLED", "0") == "1")
    CELERY_ALWAYS_EAGER = False
    CELERY_ACKS_LATE = True
    CELERY_TASK_PUBLISH_RETRY = True
    CELERY_DISABLE_RATE_LIMITS = False

    # timeout for getting task results
    CELERY_GET_RESULT_TIMEOUT = 1.0

    # If you want to see results and try out tasks interactively,
    # change it to False
    # Or change this setting on tasks level
    # CELERY_IGNORE_RESULT = True
    CELERY_SEND_TASK_ERROR_EMAILS = False
    # CELERY_TASK_RESULT_EXPIRES = 600

    # Set redis as celery result backend
    CELERY_BROKER_URL = os.getenv(
        "BROKER_URL",
        ("redis://{}:{}/{}").format(
            REDIS_HOST,
            REDIS_PORT,
            REDIS_BROKER_DB))
    CELERY_RESULT_BACKEND = os.getenv(
        "BACKEND_URL",
        ("redis://{}:{}/{}").format(
            REDIS_HOST,
            REDIS_PORT,
            REDIS_RESULT_DB))

    # CELERY_REDIS_MAX_CONNECTIONS = 1

    # Do not use pickle as serializer, json is much safer
    CELERY_TASK_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["application/json"]

    CELERYD_HIJACK_ROOT_LOGGER = False
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERYD_MAX_TASKS_PER_CHILD = 1000

    # Django Cacheops
    # https://github.com/Suor/django-cacheops
    # https://github.com/Suor/django-cacheops/blob/master/LICENSE
    CACHEOPS_ENABLED = bool(os.environ.get("CACHEOPS_ENABLED", "0") == "1")
    if CACHEOPS_ENABLED:
        CACHEOPS_REDIS = {
            "host": os.getenv(
                "REDIS_CACHE_HOST",
                REDIS_HOST),
            "port": int(os.getenv(
                "REDIS_CACHE_PORT",
                REDIS_PORT)),
            "db": int(os.getenv(
                "REDIS_CACHE_DB",
                "8")),
            "socket_timeout": int(os.getenv(
                "REDIS_CACHE_TIMEOUT",
                "3"))
        }
        CACHEOPS_DEFAULTS = {
            "timeout": 60*60
        }
        CACHEOPS = {
            "auth.user": {"ops": "get", "timeout": 60*15},
            "auth.*": {"ops": ("fetch", "get")},
            "auth.permission": {"ops": "all"},
            "*.*": {},
        }
    # end of if CACHEOPS_ENABLED

    # AntiNex Worker settings - Optional
    ANTINEX_API_NAME = os.getenv(
        "ANTINEX_API_SOURCE_NAME",
        "drf")
    ANTINEX_WORKER_ENABLED = bool(os.getenv(
        "ANTINEX_WORKER_ENABLED", "0") == "1")

    # bypass the django train + predict and only use the worker
    # note - no predictions will be stored in the database
    ANTINEX_WORKER_ONLY = bool(os.getenv(
        "ANTINEX_WORKER_ONLY", "0") == "1")

    ANTINEX_AUTH_URL = os.getenv(
        "ANTINEX_AUTH_URL", "redis://localhost:6379/6")
    ANTINEX_RESULT_AUTH_URL = os.getenv(
        "ANTINEX_RESULT_AUTH_URL", "redis://localhost:6379/9")

    # AntiNex routing
    ANTINEX_EXCHANGE_NAME = os.getenv(
        "ANTINEX_EXCHANGE_NAME", "webapp.predict.requests")
    ANTINEX_EXCHANGE_TYPE = os.getenv(
        "ANTINEX_EXCHANGE_TYPE", "topic")
    ANTINEX_ROUTING_KEY = os.getenv(
        "ANTINEX_ROUTING_KEY", "webapp.predict.requests")
    ANTINEX_QUEUE_NAME = os.getenv(
        "ANTINEX_QUEUE_NAME", "webapp.predict.requests")
    ANTINEX_RESULT_EXCHANGE_NAME = os.getenv(
        "ANTINEX_RESULT_EXCHANGE_NAME",
        "drf_network_pipeline.pipeline.tasks.task_ml_process_results")
    ANTINEX_RESULT_EXCHANGE_TYPE = os.getenv(
        "ANTINEX_RESULT_EXCHANGE_TYPE", "topic")
    ANTINEX_RESULT_ROUTING_KEY = os.getenv(
        "ANTINEX_RESULT_ROUTING_KEY",
        "drf_network_pipeline.pipeline.tasks.task_ml_process_results")
    ANTINEX_RESULT_QUEUE_NAME = os.getenv(
        "ANTINEX_RESULT_QUEUE_NAME",
        "drf_network_pipeline.pipeline.tasks.task_ml_process_results")
    ANTINEX_RESULT_TASK_NAME = os.getenv(
        "ANTINEX_RESULT_TASK_NAME",
        "drf_network_pipeline.pipeline.tasks.task_ml_process_results")

    # By default persist messages to disk
    ANTINEX_PERSISTENT_MESSAGES = 2
    ANTINEX_NON_PERSISTENT_MESSAGES = 1
    ANTINEX_DELIVERY_MODE = ANTINEX_PERSISTENT_MESSAGES
    ANTINEX_RESULT_DELIVERY_MODE = ANTINEX_PERSISTENT_MESSAGES
    antinex_default_delivery_method = os.getenv(
        "ANTINEX_DELIVERY_MODE",
        "persistent").lower()
    if antinex_default_delivery_method != "persistent":
        ANTINEX_DELIVERY_MODE = ANTINEX_NON_PERSISTENT_MESSAGES
        ANTINEX_RESULT_DELIVERY_MODE = ANTINEX_NON_PERSISTENT_MESSAGES

    # AntiNex SSL Configuration - Not Required for Redis
    ANTINEX_WORKER_SSL_ENABLED = bool(os.getenv(
        "ANTINEX_WORKER_SSL_ENABLED", "0") == "1")

    antinex_default_ca_certs = "/etc/pki/ca-trust/source/anchors/antinex.ca"
    antinex_default_keyfile = "/etc/pki/tls/private/antinex.io.crt"
    antinex_default_certfile = "/etc/pki/tls/certs/antinex.io.pem"

    ANTINEX_CA_CERTS = os.getenv(
        "ANTINEX_CA_CERTS", None)
    ANTINEX_KEYFILE = os.getenv(
        "ANTINEX_KEYFILE", None)
    ANTINEX_CERTFILE = os.getenv(
        "ANTINEX_CERTFILE", None)
    ANTINEX_TLS_PROTOCOL = ssl.PROTOCOL_TLSv1_2
    ANTINEX_CERT_REQS = ssl.CERT_REQUIRED

    antinex_tls_protocol_str = os.getenv(
        "ANTINEX_TLS_PROTOCOL", "tls1.2")
    if antinex_tls_protocol_str == "tls1":
        ANTINEX_TLS_PROTOCOL = ssl.PROTOCOL_TLSv1
    elif antinex_tls_protocol_str == "tls1.1":
        ANTINEX_TLS_PROTOCOL = ssl.PROTOCOL_TLSv1_1

    antinex_cert_reqs_str = os.getenv(
        "ANTINEX_CERT_REQS", "CERT_REQUIRED").lower()
    if antinex_cert_reqs_str == "cert_none":
        ANTINEX_CERT_REQS = ssl.CERT_NONE
    elif antinex_cert_reqs_str == "cert_optional":
        ANTINEX_CERT_REQS = ssl.CERT_OPTIONAL

    ANTINEX_SSL_OPTIONS = {}
    ANTINEX_RESULT_SSL_OPTIONS = {}
    if ANTINEX_WORKER_SSL_ENABLED:
        ANTINEX_SSL_OPTIONS = {
            "ssl_version": ANTINEX_TLS_PROTOCOL,
            "cert_reqs": ANTINEX_CERT_REQS
        }
        if ANTINEX_CA_CERTS:
            ANTINEX_SSL_OPTIONS["ca_certs"] = ANTINEX_CA_CERTS
        if ANTINEX_KEYFILE:
            ANTINEX_SSL_OPTIONS["keyfile"] = ANTINEX_KEYFILE
        if ANTINEX_CERTFILE:
            ANTINEX_SSL_OPTIONS["certfile"] = ANTINEX_CERTFILE
    # end of setting if ssl is enabled

    ANTINEX_RESULT_SSL_OPTIONS = ANTINEX_SSL_OPTIONS

    # end of AntiNex Worker settings

    # Add custom routing here
    CELERY_CREATE_MISSING_QUEUES = True
    CELERY_QUEUES = (
        Queue(
            "default",
            Exchange("default"),
            routing_key="default"),
        Queue(
            ("drf_network_pipeline.users.tasks."
             "task_get_user"),
            Exchange(
                "drf_network_pipeline.users.tasks."
                "task_get_user"),
            routing_key=(
                "drf_network_pipeline.users.tasks."
                "task_get_user")),
        Queue(
            ("drf_network_pipeline.pipeline.tasks."
             "task_ml_prepare"),
            Exchange(
                "drf_network_pipeline.pipeline.tasks."
                "task_ml_prepare"),
            routing_key=(
                "drf_network_pipeline.pipeline.tasks."
                "task_ml_prepare")),
        Queue(
            ("drf_network_pipeline.pipeline.tasks."
             "task_ml_job"),
            Exchange(
                "drf_network_pipeline.pipeline.tasks."
                "task_ml_job"),
            routing_key=(
                "drf_network_pipeline.pipeline.tasks."
                "task_ml_job")),
        Queue(
            ("drf_network_pipeline.pipeline.tasks."
             "task_ml_process_results"),
            Exchange(
                "drf_network_pipeline.pipeline.tasks."
                "task_ml_process_results"),
            routing_key=(
                "drf_network_pipeline.pipeline.tasks."
                "task_ml_process_results")),
        Queue(
            ("drf_network_pipeline.pipeline.tasks."
             "task_publish_to_core"),
            Exchange(
                "drf_network_pipeline.pipeline.tasks."
                "task_publish_to_core"),
            routing_key=(
                "drf_network_pipeline.pipeline.tasks."
                "task_publish_to_core"))
    )

    CELERY_ROUTES = {
        ("drf_network_pipeline.users.tasks."
         "task_get_user"): {
            "queue":
                ("drf_network_pipeline.users.tasks."
                 "task_get_user")
        },
        ("drf_network_pipeline.pipeline.tasks."
         "task_ml_prepare"): {
            "queue":
                ("drf_network_pipeline.pipeline.tasks."
                 "task_ml_prepare")
        },
        ("drf_network_pipeline.pipeline.tasks."
         "task_ml_job"): {
            "queue":
                ("drf_network_pipeline.pipeline.tasks."
                 "task_ml_job")
        },
        ("drf_network_pipeline.pipeline.tasks."
         "task_publish_to_core"): {
            "queue":
                ("drf_network_pipeline.pipeline.tasks."
                 "task_publish_to_core")
        },
        ("drf_network_pipeline.pipeline.tasks."
         "task_ml_process_results"): {
            "queue":
                ("drf_network_pipeline.pipeline.tasks."
                 "task_ml_process_results")
        }
    }

    TEMPLATE_DIRS = [
        "drf_network_pipeline/templates"
    ]
    INCLUDE_DOCS = bool(os.getenv(
        "INCLUDE_DOCS",
        "1") == "1")
    if INCLUDE_DOCS:
        DOCS_ROOT = os.path.join(
            BASE_DIR,
            "{}/drf_network_pipeline/docs/build/html".format(
                BASE_DIR))
        DOCS_ACCESS = "public"
        DOC_START_DIR = "drf_network_pipeline/docs/build/html"
        TEMPLATE_DIRS.append(
            DOC_START_DIR
        )
        # noqa https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
        ADD_THESE_DOC_DIRS = []
        for d in os.walk(DOC_START_DIR):
            if "static" not in d[0]:
                ADD_THESE_DOC_DIRS.append(d[0])

        DEFAULT_DOC_INDEX_HTML = "{}/{}".format(
            BASE_DIR,
            "drf_network_pipeline/docs/build/html/index.html")

        TEMPLATE_DIRS = TEMPLATE_DIRS + ADD_THESE_DOC_DIRS
        if not os.path.exists(DEFAULT_DOC_INDEX_HTML):
            print(("Failed to find sphinx index "
                   "BASE_DIR={} full_path={} docs "
                   "failed to load")
                  .format(
                      BASE_DIR,
                      DEFAULT_DOC_INDEX_HTML))
    # end of adding sphinx docs into the server

# end of Common


class Development(Common):
    """
    The in-development settings and the default configuration.
    """
    DEBUG = bool(os.getenv(
        'DJANGO_DEBUG',
        'yes') == 'yes')

    TEMPLATE_DEBUG = bool(os.getenv(
        'DJANGO_TEMPLATE_DEBUG',
        'yes') == 'yes')

    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "webapp",
        "dev.antinex",
        "api.antinex.com"
    ]

    env_allowed_hosts = os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        None)
    if env_allowed_hosts:
        ALLOWED_HOSTS = env_allowed_hosts.split(",")

    INTERNAL_IPS = [
        "127.0.0.1"
    ]

    MIDDLEWARE = Common.MIDDLEWARE + [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ]


class Staging(Common):
    """
    The in-staging settings.
    """
    # Security
    SESSION_COOKIE_SECURE = values.BooleanValue(True)
    SECURE_BROWSER_XSS_FILTER = values.BooleanValue(True)
    SECURE_CONTENT_TYPE_NOSNIFF = values.BooleanValue(True)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = values.BooleanValue(True)
    SECURE_HSTS_SECONDS = values.IntegerValue(31536000)
    SECURE_REDIRECT_EXEMPT = values.ListValue([])
    SECURE_SSL_HOST = values.Value(None)
    SECURE_SSL_REDIRECT = values.BooleanValue(True)
    SECURE_PROXY_SSL_HEADER = values.TupleValue(
        ("HTTP_X_FORWARDED_PROTO", "https")
    )


class Production(Staging):
    """
    The in-production settings.
    """
    pass
