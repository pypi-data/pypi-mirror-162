########################################################################################################################
# IMPORTS

import configparser
import logging
import random
import shlex
import subprocess
import time

########################################################################################################################
# FUNCTIONS

logger = logging.getLogger(__name__)


def get_config(config_path):
    cfg = configparser.RawConfigParser()
    cfg.read(config_path)
    return cfg


def set_logger(level):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(level.upper())
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    log.addHandler(ch)


def ban_sleep(max_time, min_time=0):
    sleep_time = int(random.uniform(min_time, max_time))
    logger.info(f"sleeping for {sleep_time} seconds...")
    time.sleep(sleep_time)


def run_bash_command(command):
    p = subprocess.Popen(
        shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for line_b in iter(p.stdout.readline, ""):
        line_str = line_b.decode().strip()

        if not line_str:
            break

        logger.info(line_str)
