from bs4 import BeautifulSoup
import requests
import json
from utils.func import *


class PatentsView:
    def __init__(self):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36",
        }
        self.proxies = {
            "https": "http://10.8.14.229:7890",
            "http": "http://10.8.14.229:7890"
        }
        self._granted_url = "https://patentsview.org/download/data-download-tables"
        self._brief_sum_url = "https://patentsview.org/download/brf_sum_text"
        self._claims_url = "https://patentsview.org/download/claims"
        self._detail_desc_url = "https://patentsview.org/download/detail_desc_text"
        self._draw_desc_url = "https://patentsview.org/download/draw_desc_text"
        self._data_path = "./data.json"
        self._update_data = None
        self._load_last_check_data()

    def _load_last_check_data(self):
        with open(self._data_path) as file:
            last_data = json.load(file)
        self._last_update_data = last_data

    def _get_granted(self):
        page = requests.get(url=self._granted_url, proxies=self.proxies)
        html = page.text.encode().decode()
        bs_obj = BeautifulSoup(html, "lxml")
        trs = bs_obj.select("#myTable > tbody > tr")
        granted_data = {}
        for tr in trs:
            table_name_item = tr.select(
                "td.views-field.views-field-title > div > div.file-title > a")
            table_name = table_name_item[0].getText()
            table_dl_url = table_name_item[0].get("href")

            size = tr.select(
                "td.views-field.views-field-title > div > div.data-file-size")[0].getText().split()
            zip_size = eval(size[1])
            zip_size_type = size[2]
            tsv_size = eval(size[4])
            tsv_size_type = size[5]

            if zip_size_type == "MiB":
                zip_size /= 1024
            elif zip_size_type == "KiB":
                zip_size /= (1024 * 1024)
            if tsv_size_type == "MiB":
                tsv_size /= 1024
            if tsv_size_type == "KiB":
                tsv_size /= (1024 * 1024)

            update_version = tr.select(
                "td.views-field.views-field-field-update-version > time")[0].getText()
            granted_data.update({
                table_name: {
                    "url": table_dl_url,
                    "zip": zip_size,
                    "tsv": tsv_size,
                    "update_version": update_version
                }
            })
        return granted_data

    def _get_long_text(self, long_text_table_url):
        page = requests.get(url=long_text_table_url, proxies=self.proxies)
        html = page.text.encode().decode()
        bs_obj = BeautifulSoup(html, "lxml")
        divs = bs_obj.select("#download-table > div.data-grid > div")
        data = {}
        for div_obj in divs:
            class_type = div_obj.get("class")
            if class_type is not None and class_type[0] == "data-header":
                continue

            year_item = div_obj.select("a")[0]
            year = year_item.getText()

            zip_size, zip_size_type = div_obj.select(
                "div.filesize.file-mb")[0].getText()[4:].split()
            zip_size = eval(zip_size)

            tsv_size, tsv_size_type = div_obj.select(
                "div:nth-child(3)")[0].getText()[4:].split()
            tsv_size = eval(tsv_size)

            if zip_size_type == "MiB":
                zip_size /= 1024
            elif zip_size_type == "KiB":
                zip_size /= (1024 * 1024)
            if tsv_size_type == "MiB":
                tsv_size /= 1024
            if tsv_size_type == "KiB":
                tsv_size /= (1024 * 1024)

            dl_url = year_item.get("href")
            update_version = div_obj.select(
                "div.filesize.file-date")[0].getText()

            data.update({
                year: {
                    "url": dl_url,
                    "zip": zip_size,
                    "tsv": tsv_size,
                    "update_version": update_version
                }
            })
        return data

    def update_data(self):
        self._load_last_check_data()

    def save_check_data(self):
        with open(self._data_path, "w") as file:
            json.dump(self._update_data, file)

    def check_last_updated(self):
        self._update_data = {}

        iprint("Checking Granted Patents")
        granted_data = self._get_granted()
        self._update_data.update({"Granted patents": granted_data})

        long_text_dl_urls = {
            "Brief Summary Text": self._brief_sum_url,
            "Claim": self._claims_url,
            "Detail Description Text": self._detail_desc_url,
            "Drawing Description Text": self._draw_desc_url
        }
        for long_text in long_text_dl_urls:
            iprint("Checking {}".format(long_text))
            data = self._get_long_text(long_text_dl_urls[long_text])
            self._update_data.update({long_text: data})

        return self._update_data

    def compare_diff(self, save_sh=True):
        sh_content = ""
        dl_urls = []
        for data_type in self._update_data:
            current_tables = self._update_data[data_type]
            old_tables = self._last_update_data[data_type]
            for table_name in current_tables:
                if table_name in old_tables:
                    last_version = old_tables[table_name]["update_version"]
                    cur_version = current_tables[table_name]["update_version"]
                    if last_version == cur_version:
                        iprint(
                            "{}-{} already up to date".format(data_type, table_name))
                    else:
                        iprint("{}-{} changed, update to {}".format(
                            data_type, table_name, cur_version))
                        sh_content += "wget -P dl/ {}\n".format(
                            current_tables[table_name]["url"])
                        dl_urls.append(current_tables[table_name]["url"])
                else:
                    iprint("{}-{} added, update to {}".format(
                        data_type, table_name, cur_version))
                    sh_content += "wget -P dl/ {}\n".format(
                        current_tables[table_name]["url"])
                    dl_urls.append(current_tables[table_name]["url"])

        if save_sh:
            with open("dl.sh", "w") as sh:
                sh.write(sh_content)

        return dl_urls

    def gen_all_download_url(self, save_sh=True):
        self.check_last_updated()
        sh_content = ""
        dl_urls = []
        for data_type in self._update_data:
            current_tables = self._update_data[data_type]
            for table_name in current_tables:
                sh_content += "wget -P dl/ {}\n".format(
                    current_tables[table_name]["url"])
                dl_urls.append(current_tables[table_name]["url"])
        if save_sh:
            with open("dl.sh", "w") as sh:
                sh.write(sh_content)
        return dl_urls

    def analyze(self):
        total_num = 0
        total_zip_size = 0
        total_tsv_size = 0
        for data_type in self._update_data:
            current_tables = self._update_data[data_type]
            total_num += len(current_tables)
            for table_name in current_tables:
                total_zip_size += current_tables[table_name]["zip"]
                total_tsv_size += current_tables[table_name]["tsv"]
                dprint(total_tsv_size)
        return total_num, round(total_zip_size, 3), round(total_tsv_size, 3)

    def test(self):
        iprint(self._get_long_text(self._brief_sum_url))


if __name__ == "__main__":
    p = PatentsView()
    p.gen_all_download_url()
