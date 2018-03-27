from django.db.models import Q
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
        body=None):
    """handle_worker_results_message
    :param body: contents from the results
    """
    label = "APIRES"
    last_step = ""
    try:
        last_step = ("{} received worker results body={}").format(
                        label,
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

# end of handle_worker_results_message


def process_worker_results(
        res_node=None):
    """process_worker_results

    :param res_node: incoming request dictionary - not used right now
    """

    status = SUCCESS
    api_node = build_worker_result_node()

    # the worker is disabled - nothing to process
    if not api_node:
        return status

    label = "APIRES"
    last_step = "not-started"

    try:

        last_step = ("{} - start").format(
            label)
        log.info(last_step)

        handle_worker_results_message(
            body=res_node)

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

    return status
# end of process_worker_results
