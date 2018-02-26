import os
import json
import logging.config


def setup_logging(default_level=logging.INFO,
                  default_path="{}/logging.json".format(
                      os.getenv(
                          "LOG_DIR",
                          os.path.dirname(os.path.realpath(__file__)))),
                  env_key="LOG_CFG",
                  config_name=None):

    """
    Setup logging configuration
    """
    path = default_path
    file_name = default_path.split("/")[-1]
    if config_name:
        file_name = config_name

    path = "{}/{}".format(
                "/".join(default_path.split("/")[:-1]),
                file_name)

    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        return

    else:
        cwd_path = os.getcwd() + "/network_pipeline/log/{}".format(
                                    file_name)
        if os.path.exists(cwd_path):
            with open(cwd_path, "rt") as f:
                config = json.load(f)
            logging.config.dictConfig(config)
            return
        rels_path = os.getcwd() + "/../log/{}".format(
                                    file_name)
        if os.path.exists(rels_path):
            with open(rels_path, "rt") as f:
                config = json.load(f)
            logging.config.dictConfig(config)
            return
        else:
            logging.basicConfig(level=default_level)
            return
# end of setup_logging


def build_logger(
    name=os.getenv(
        "LOG_NAME",
        "worker"),
    config="logging.json",
    log_level=logging.INFO,
    log_config_path="{}/logging.json".format(
        os.getenv(
            "LOG_CFG",
            os.path.dirname(os.path.realpath(__file__))))):
    """build_logger

    :param name: name that shows in the logger
    :param config: name of the config file
    :param log_level: level to log
    :param log_config_path: path to log config file
    """
    use_config = ("./log/{}").format(
                    "{}".format(
                        config))
    if not os.path.exists(use_config):
        use_config = log_config_path
        if not os.path.exists(use_config):
            use_config = ("./drf_network_pipeline/log/{}").format(
                            "logging.json")
    # find the log processing

    setup_logging(
        default_level=log_level,
        default_path=use_config)

    return logging.getLogger(name)
# end of build_logger


def build_colorized_logger(
    name=os.getenv(
        "LOG_NAME",
        "worker"),
    config="colors-logging.json",
    log_level=logging.INFO,
    log_config_path="{}/logging.json".format(
        os.getenv(
            "LOG_CFG",
            os.path.dirname(os.path.realpath(__file__))))):
    """build_colorized_logger

    :param name: name that shows in the logger
    :param config: name of the config file
    :param log_level: level to log
    :param log_config_path: path to log config file
    """
    use_config = ("./log/{}").format(
                    "{}".format(
                        config))
    if not os.path.exists(use_config):
        use_config = log_config_path
        if not os.path.exists(use_config):
            use_config = ("./drf_network_pipeline/log/{}").format(
                            "logging.json")
    # find the log processing

    setup_logging(
        default_level=log_level,
        default_path=use_config)

    return logging.getLogger(name)
# end of build_colorized_logger
