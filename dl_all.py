from utils.PatentsView import PatentsView
from utils.func import *


if __name__ == "__main__":
    log_level = logging.INFO
    logger_file = None
    create_logger(log_level, logger_file)

    patents_view = PatentsView()

    all_urls = patents_view.gen_all_download_url()
    download_all_urls(all_urls)
