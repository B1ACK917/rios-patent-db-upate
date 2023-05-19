import glob
import os
import subprocess
import pandas as pd
import argparse
from utils.func import *
# 263270

parser = argparse.ArgumentParser(description="tsv to csv")
parser.add_argument('-d', '--dir', type=str, help='work dir')


def process(workpath):
    os.chdir(workpath)
    zip_files = glob.glob("*.zip")
    total_num = len(zip_files)
    iprint("Removing old files")
    subprocess.run(["rm", "*.tsv", "*.csv"])

    for i, zip_file in enumerate(zip_files):
        file_name, _, __ = zip_file.split(".")
        tsv_file = "{}.tsv".format(file_name)
        csv_file = "{}.csv".format(file_name)
        csv_dir = "../csv"
        if not os.path.exists(csv_dir):
            os.mkdir(csv_dir)

        iprint("Begin to process {}, [{}/{}]".format(zip_file, i+1, total_num))

        subprocess.run(["unzip", zip_file])

        iprint("Translating tsv to csv")
        data = pd.read_csv(tsv_file, sep='\t')
        data.to_csv(f"{file_name}.csv")

        iprint("Putting csv to HDFS")
        if file_name.startswith("g_brf_sum_text"):
            subprocess.run(["hdfs", "dfs", "-put", csv_file,
                           "/patent/uspto/g_brf_sum_text/"])
        elif file_name.startswith("g_claims"):
            subprocess.run(["hdfs", "dfs", "-put", csv_file,
                           "/patent/uspto/g_claims/"])
        elif file_name.startswith("g_detail_desc_text"):
            subprocess.run(["hdfs", "dfs", "-put", csv_file,
                           "/patent/uspto/g_detail_desc_text/"])
        elif file_name.startswith("g_draw_desc_text"):
            subprocess.run(["hdfs", "dfs", "-put", csv_file,
                           "/patent/uspto/g_draw_desc_text/"])
        else:
            subprocess.run(
                ["hdfs", "dfs", "-put", csv_file, "/patent/uspto/csv/"])

        iprint("Removing tsv file {}".format(tsv_file))
        subprocess.run(["rm", tsv_file])

        iprint("Moving {} to ../csv folder".format(csv_file))
        subprocess.run(["mv", csv_file, os.path.join(csv_dir, csv_file)])


if __name__ == "__main__":
    log_level = logging.INFO
    logger_file = None
    create_logger(log_level, logger_file)

    args = parser.parse_args()
    process(args.dir)
