import socket
from django.db.models import Q
from kombu import Connection
from kombu import Exchange
from kombu import Queue
from kombu import Consumer
from antinex_utils.consts import SUCCESS
from antinex_utils.consts import ERROR
from antinex_utils.log.setup_logging import build_colorized_logger
from drf_network_pipeline.pipeline.build_worker_result_node import \
    build_worker_result_node
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLJobResult


name = "ml_prc_results"
log = build_colorized_logger(name=name)


def handle_worker_results_message(
        body,
        message):
    """handle_worker_results_message
    :param body: contents of the message
    :param message: message object
    """
    label = "APIRES"
    last_step = ""
    try:
        last_step = ("{} received worker results from routing_key={} "
                     "body={}").format(
                        label,
                        message.delivery_info["routing_key"],
                        str(body)[0:32])
        log.info(last_step)

        manifest = body.get(
            "manifest",
            None)
        parent_result_node = body.get(
            "results",
            None)
        result = parent_result_node.get(
            "data",
            None)

        job_id = int(manifest["job_id"])
        result_id = int(manifest["result_id"])

        job_query = (Q(id=job_id))
        result_query = (Q(id=result_id))
        db_job = MLJob.objects.select_related() \
            .filter(job_query).first()
        db_result = MLJobResult.objects.select_related() \
            .filter(result_query).first()

        log.info(("{} updating job_id={} result_id={}")
                 .format(
                    label,
                    job_id,
                    result_id))

        model_json = result["model_json"]
        model_weights = result["weights"]
        scores = result["scores"]
        acc_data = result["acc"]
        error_data = result["err"]
        predictions_json = {
            "predictions": result["sample_predictions"]
        }
        acc_data = {
            "accuracy": scores[1] * 100
        }

        db_result.acc_data = acc_data
        db_result.error_data = error_data
        db_result.model_json = model_json
        db_result.model_weights = model_weights
        db_result.predictions_json = predictions_json

        db_job.status = "finished"
        db_job.control_state = "finished"
        db_result.status = "finished"
        db_result.control_status = "finished"

        log.info(("saving job_id={}")
                 .format(
                    job_id))
        db_job.save()
        log.info(("saving result_id={}")
                 .format(
                    result_id))
        db_result.save()

    except Exception as e:
        log.error(("{} failed handling worker results for body={} "
                   "last_step='{}' ex={}").format(
                    label,
                    body,
                    last_step,
                    e))
    # try/ex handling for updating the db

    message.ack()
# end of handle_worker_results_message


def process_worker_results(
        req=None):
    """process_worker_results

    :param req: incoming request dictionary - not used right now
    """

    status = SUCCESS
    api_node = build_worker_result_node()

    # the worker is disabled - nothing to process
    if not api_node:
        return status

    label = "APIRES"
    last_step = "not-started"

    conn = None

    try:

        last_step = ("{} - start").format(
            label)
        log.info(last_step)

        auth_url = api_node["auth_url"]
        ssl_options = api_node["ssl_options"]
        exchange_name = api_node["exchange"]
        exchange_type = api_node["exchange_type"]
        routing_key = api_node["routing_key"]
        queue_name = api_node["queue"]

        last_step = ("{} - connecting").format(
            label)
        log.info(last_step)

        if len(ssl_options) > 0:
            conn = Connection(
                auth_url,
                login_method="EXTERNAL",
                ssl=ssl_options,
                heartbeat=120)
        else:
            conn = Connection(
                auth_url,
                heartbeat=120)
        # end of connecting

        conn.connect()

        last_step = ("{} - getting channel").format(
            label)
        log.info(last_step)

        channel = conn.channel()

        last_step = ("{} - setting up exchange={}").format(
            label,
            exchange_name)
        log.info(last_step)

        res_exchange = Exchange(
            exchange_name,
            type=exchange_type,
            durable=True)

        last_step = ("{} - declaring exchange={}").format(
            label,
            exchange_name)
        log.info(last_step)

        # noqa http://docs.celeryproject.org/projects/kombu/en/latest/reference/kombu.html#exchange
        try:
            bound_exchange = res_exchange(channel)
            bound_exchange.declare()
        except Exception as f:
            log.info(("exchange={} declare failed with ex={}")
                     .format(
                        exchange_name,
                        f))
        # end of try/ex for exchange

        last_step = ("{} - setting up queue={} routing_key={}").format(
            label,
            queue_name,
            routing_key)
        log.info(last_step)

        consume_this_queue = Queue(
            queue_name,
            res_exchange,
            routing_key=routing_key,
            durable=True)

        last_step = ("{} - binding and declaring queue={}").format(
            label,
            queue_name,
            routing_key)
        log.info(last_step)

        try:
            consume_this_queue.maybe_bind(conn)
            consume_this_queue.declare()
        except Exception as f:
            log.info(("queue={} declare failed with ex={}")
                     .format(
                        queue_name,
                        f))
        # end of try/ex for exchange

        last_step = ("{} - setting up consumer for queue={}").format(
            label,
            queue_name)
        log.info(last_step)

        consumer = Consumer(
            conn,
            queues=[consume_this_queue],
            auto_declare=True,
            callbacks=[handle_worker_results_message],
            accept=["json"])

        last_step = ("{} - consuming from queue={}").format(
            label,
            queue_name)
        log.info(last_step)

        not_done = True
        time_to_wait = 0.1
        num_attempts = 5
        cur_attempt = 1
        while not_done:
            if cur_attempt > num_attempts:
                log.info(("{} - max attempts")
                         .format(
                            label))
                not_done = False
                break
            cur_attempt += 1
            try:
                log.info(("{} consuming")
                         .format(
                            label))
                consumer.consume()
                conn.drain_events(
                    timeout=time_to_wait)
            except socket.timeout:
                conn.heartbeat_check()
                not_done = False
            except Exception as f:
                log.error(("{} consumer hit ex={}")
                          .format(
                            label,
                            f))
                not_done = False
        # while not done consuming

        log.info(("{} done")
                 .format(
                    label))

    except Exception as e:
        log.error(("{} failed processing core results last_step='{}' ex={}")
                  .format(
                    label,
                    last_step,
                    e))
        status = ERROR
    # end of try/ex

    if conn:
        conn.close()

    return status
# end of process_worker_results
