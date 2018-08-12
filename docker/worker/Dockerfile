FROM jayjohnson/ai-core:latest

RUN echo "preparing image and building" \
  && mkdir -p -m 777 /var/log/antinex/api \
  && mkdir -p -m 777 /opt/antinex \
  && chmod 777 //var/log/antinex/api \
  && touch /var/log/antinex/api/worker.log \
  && touch /var/log/antinex/api/api.log \
  && chmod 777 /var/log/antinex/api/worker.log \
  && chmod 777 /var/log/antinex/api/api.log \
  && echo "updating repo" \
  && cd /opt/antinex/api \
  && git checkout master \
  && git pull \
  && echo "checking repo in container" \
  && ls -l /opt/antinex/api \
  && echo "activating venv" \
  && . /opt/venv/bin/activate \
  && cd /opt/antinex/api \
  && echo "installing pip upgrades" \
  && pip install --upgrade -r /opt/antinex/api/requirements.txt \
  && echo "building docs" \
  && cd /opt/antinex/api/webapp/drf_network_pipeline/docs \
  && pip install -r /opt/antinex/api/webapp/drf_network_pipeline/docs/doc-requirements.txt

RUN echo "Downgrading numpy and setuptools for tensorflow" \
  && . /opt/venv/bin/activate \
  && pip install --upgrade numpy==1.14.5 \
  && pip install --upgrade setuptools==39.1.0

RUN echo "Making Sphinx docs" \
  && . /opt/venv/bin/activate \
  && cd /opt/antinex/api/webapp/drf_network_pipeline/docs \
  && ls -l \
  && make html

ENV PROJECT_NAME="api" \
    SHARED_LOG_CFG="/opt/antinex/core/antinex_core/log/debug-openshift-logging.json" \
    DEBUG_SHARED_LOG_CFG="0" \
    LOG_LEVEL="DEBUG" \
    LOG_FILE="/var/log/antinex/api/worker.log" \
    USE_ENV="drf-dev" \
    USE_VENV="/opt/venv" \
    API_USER="trex" \
    API_PASSWORD="123321" \
    API_EMAIL="bugs@antinex.com" \
    API_FIRSTNAME="Guest" \
    API_LASTNAME="Guest" \
    API_URL="http://api.antinex.com:8010" \
    API_VERBOSE="true" \
    API_DEBUG="false" \
    USE_FILE="false" \
    SILENT="-s" \
    RUN_API="/opt/antinex/api/run-django.sh" \
    RUN_WORKER="/opt/antinex/api/run-worker.sh"

WORKDIR /opt/antinex/api

# set for anonymous user access in the container
RUN find /opt/antinex/api -type d -exec chmod 777 {} \;
RUN find /var/log/antinex -type d -exec chmod 777 {} \;

ENTRYPOINT . /opt/venv/bin/activate \
  && /opt/antinex/api \
  && ${RUN_WORKER}
