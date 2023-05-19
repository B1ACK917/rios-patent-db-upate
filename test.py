from utils.PatentsView import PatentsView
from utils.func import *


if __name__ == "__main__":
    log_level = logging.INFO
    logger_file = None
    create_logger(log_level, logger_file)

    patents_view = PatentsView()

    patents_view.check_last_updated()
    patents_view.save_check_data()
    num, zip_sz, tsv_sz = patents_view.analyze()
    iprint("{} Tables, zip: {} GB, tsv: {} GB".format(num, zip_sz, tsv_sz))
