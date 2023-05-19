import logging
import os
import sys
import wget
import urllib
import ssl
import subprocess

cur_logger = None
ssl._create_default_https_context = ssl._create_unverified_context


def iprint(*args, **kwargs):
    if isinstance(cur_logger, logging.Logger):
        return cur_logger.info(*args, **kwargs)
    else:
        return print(*args, **kwargs)


def dprint(*args, **kwargs):
    if isinstance(cur_logger, logging.Logger):
        return cur_logger.debug(*args, **kwargs)
    else:
        return print(*args, **kwargs)


def create_logger(log_level, log_file=None):
    global cur_logger
    # Create a custom logger
    logger = logging.getLogger("Database AutoUpdater")
    logger.setLevel(log_level)

    c_handler = logging.StreamHandler(stream=sys.stdout)
    c_handler.setLevel(log_level)

    # Create formatters and add it to handlers
    c_format = logging.Formatter(
        '[%(asctime)s][%(name)s][%(levelname)s][%(message)s]')
    c_handler.setFormatter(c_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)

    # Process only if log file defined
    if log_file is not None:
        f_handler = logging.FileHandler(log_file)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s][%(message)s]')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)

    cur_logger = logger
    return logger


def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_filename(path):
    return os.path.splitext(os.path.basename(path))[0]


def download_all_urls(dl_urls, skip_exist=True, replace=True):
    exist_files = os.listdir("./dl")
    total_num = len(dl_urls)
    for i, dl_url in enumerate(dl_urls):
        dl_name = dl_url.split("/")[-1]
        if skip_exist and (dl_name in exist_files):
            iprint("{} exists, skip downloading".format(dl_name))
            continue
        if replace and (dl_name in exist_files):
            iprint("{} exists, remove old version".format(dl_name))
            subprocess.run(["rm", os.path.join("./dl", dl_name)])
        while True:
            try:
                iprint("Begin downloading {}".format(dl_name))
                wget.download(dl_url, out="dl", bar=None)
                break
            except urllib.error.ContentTooShortError:
                iprint("Download error, retry deployed")
                continue
        iprint("{} downloaded, {}/{}".format(dl_name, i + 1, total_num))
