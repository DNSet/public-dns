# !/usr/bin/env python3

import csv
from io import TextIOWrapper
import ipaddress
import json
import os
from typing import Dict
from typing import List

SCRIPTS = os.path.dirname(__file__)
BASEDIR = os.path.dirname(SCRIPTS)
DATADIR = os.path.join(BASEDIR, "nameservers")
CNTYDIR = os.path.join(DATADIR, "countries")
IPV4DIR = os.path.join(DATADIR, "countries", "IPv4")
IPV6DIR = os.path.join(DATADIR, "countries", "IPv6")
JSONDIR = os.path.join(DATADIR, "json")
TXTDIR = os.path.join(DATADIR, "txt")
CSVDIR = os.path.join(DATADIR, "csv")

for _dir in [DATADIR, CNTYDIR, IPV4DIR, IPV6DIR]:
    if not os.path.exists(_dir):
        os.mkdir(_dir)

FIELDS = ["ip_address", "name", "as_number", "as_org", "country_code", "city",
          "version", "error", "dnssec", "reliability", "checked_at",
          "created_at"]


class Country():
    pass

    def __init__(self, country_code: str):
        assert isinstance(country_code, str)
        self.__name: str = country_code.strip().upper()
        self.__dns: List[Dict[str, str]] = list()
        self.__dns_v4: List[Dict[str, str]] = list()
        self.__dns_v6: List[Dict[str, str]] = list()
        self.__dot_csv: str = os.path.join(CNTYDIR, f"{self.name}.csv")
        self.__dot_txt: str = os.path.join(CNTYDIR, f"{self.name}.txt")
        self.__dot_json: str = os.path.join(CNTYDIR, f"{self.name}.json")
        self.__dot_csv_v4: str = os.path.join(IPV4DIR, f"{self.name}.csv")
        self.__dot_txt_v4: str = os.path.join(IPV4DIR, f"{self.name}.txt")
        self.__dot_json_v4: str = os.path.join(IPV4DIR, f"{self.name}.json")
        self.__dot_csv_v6: str = os.path.join(IPV6DIR, f"{self.name}.csv")
        self.__dot_txt_v6: str = os.path.join(IPV6DIR, f"{self.name}.txt")
        self.__dot_json_v6: str = os.path.join(IPV6DIR, f"{self.name}.json")
        self.__hdl_txt: TextIOWrapper = open(self.__dot_txt, "w")
        self.__hdl_json: TextIOWrapper = open(self.__dot_json, "w")
        self.__hdl_txt_v4: TextIOWrapper = open(self.__dot_txt_v4, "w")
        self.__hdl_json_v4: TextIOWrapper = open(self.__dot_json_v4, "w")
        self.__hdl_txt_v6: TextIOWrapper = open(self.__dot_txt_v6, "w")
        self.__hdl_json_v6: TextIOWrapper = open(self.__dot_json_v6, "w")

    def __iter__(self):
        return iter(self.__dns)

    @property
    def name(self) -> str:
        return self.__name

    def close(self):
        self.__hdl_txt.close()
        self.__hdl_json.close()
        self.__hdl_txt_v4.close()
        self.__hdl_json_v4.close()
        self.__hdl_txt_v6.close()
        self.__hdl_json_v6.close()

    def append(self, object: Dict[str, str]):
        self.__dns.append(object)
        ip_address = object["ip_address"]
        json_string = json.dumps(object)
        self.__hdl_txt.write(ip_address)
        self.__hdl_txt.write("\n")
        self.__hdl_json.write(json_string)
        self.__hdl_json.write("\n")
        ip_version = ipaddress.ip_address(ip_address).version
        if ip_version == 4:
            self.__dns_v4.append(object)
            self.__hdl_txt_v4.write(ip_address)
            self.__hdl_txt_v4.write("\n")
            self.__hdl_json_v4.write(json_string)
            self.__hdl_json_v4.write("\n")
        elif ip_version == 6:
            self.__dns_v6.append(object)
            self.__hdl_txt_v6.write(ip_address)
            self.__hdl_txt_v6.write("\n")
            self.__hdl_json_v6.write(json_string)
            self.__hdl_json_v6.write("\n")
        else:
            raise ValueError(ip_version)

    def dump_csv(self):
        with open(self.__dot_csv, "w") as hdl:
            writer = csv.DictWriter(hdl, fieldnames=FIELDS)
            writer.writeheader()
            for rowdict in self.__dns:
                writer.writerow(rowdict)
        with open(self.__dot_csv_v4, "w") as hdl:
            writer = csv.DictWriter(hdl, fieldnames=FIELDS)
            writer.writeheader()
            for rowdict in self.__dns_v4:
                writer.writerow(rowdict)
        with open(self.__dot_csv_v6, "w") as hdl:
            writer = csv.DictWriter(hdl, fieldnames=FIELDS)
            writer.writeheader()
            for rowdict in self.__dns_v6:
                writer.writerow(rowdict)


COUNTRIES: Dict[str, Country] = dict()


def add_to_country(object: Dict[str, str]):
    country_code = item["country_code"].strip().upper()
    if len(country_code) > 0:
        if country_code not in COUNTRIES:
            COUNTRIES[country_code] = Country(country_code)
        COUNTRIES[country_code].append(object)


with open(os.path.join(BASEDIR, "public-dns.info.csv"), "w") as whdl, \
        open(os.path.join(DATADIR, "nameservers-all.csv")) as rhdl:
    writer = csv.writer(whdl)
    for item in csv.DictReader(rhdl):
        as_number = int(item["as_number"])
        country_code = item["country_code"].upper()
        writer.writerow([as_number, item["as_org"], item["name"],
                         item["country_code"], item["city"],
                         item["ip_address"]])
        add_to_country(item)


for country in COUNTRIES.values():
    country.dump_csv()
    country.close()

message = "rebuild public-dns.info $(date '+%F %T')"
command = " && ".join([f"cd {BASEDIR}", f"git add {CNTYDIR}",
                       f"git commit --message=\"{message}\""])
os.system(command)
