from utils.PatentsView import PatentsView
from utils.func import *
import time


if __name__ == "__main__":
    log_level = logging.INFO
    logger_file = None
    create_logger(log_level, logger_file)

    patents_view = PatentsView()

    while True:
        patents_view.update_data()
        updated_data = patents_view.check_last_updated()
        dl_urls = patents_view.compare_diff(save_sh=False)
        patents_view.save_check_data()
        if len(dl_urls):
            download_all_urls(dl_urls, skip_exist=False, replace=True)
        else:
            iprint("Check completed, all up to date, sleep 3600s")
            time.sleep(3600)
