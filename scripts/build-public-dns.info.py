# !/usr/bin/env python3

import ipaddress
import os
from typing import Dict
from typing import Generic
from typing import Iterator
from typing import List
from typing import TypeVar

from dnsprobe import dnsprobe_nameservers
from xarg import safile

SCRIPTS = os.path.dirname(__file__)
BASEDIR = os.path.dirname(SCRIPTS)
LT = TypeVar("LT")  # Label type.


class Nameserver():

    def __init__(self, path: str, info: dnsprobe_nameservers.item):
        self.__info: dnsprobe_nameservers.item = info
        self.__path: str = path

    @property
    def path(self) -> str:
        return self.__path

    @property
    def info(self) -> dnsprobe_nameservers.item:
        return self.__info

    def dump(self) -> None:
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        assert os.path.isdir(self.path)

        def output_info(text: str) -> str:
            return text if text else "Unknown"

        path: str = os.path.join(self.path, "readme.md")
        text: str = f"""# Nameserver {self.info.ip_address}

* as_number: {self.info.as_number}
* name: {output_info(self.info.name)}
* city: {output_info(self.info.city)}
* country: {output_info(self.info.country_code)}
* organization: {output_info(self.info.as_org)}
* version: {output_info(self.info.version)}
* dnssec: {output_info(self.info.dnssec)}
"""
        assert safile.create_backup(path)
        with open(path, "w") as whdl:
            whdl.write(text)
        assert safile.dalete_backup(path)

    @classmethod
    def load(cls, path: str, info: dnsprobe_nameservers.item) -> "Nameserver":
        nameserver = Nameserver(path, info)
        return nameserver


class NameserverSet(set[Nameserver]):
    def __init__(self):
        super().__init__()

    @classmethod
    def is_ipv4(cls, ip_address: str):
        try:
            ipaddress.IPv4Address(ip_address)
            return True
        except ipaddress.AddressValueError:
            return False

    @classmethod
    def is_ipv6(cls, ip_address: str):
        try:
            ipaddress.IPv6Address(ip_address)
            return True
        except ipaddress.AddressValueError:
            return False

    def dump(self, path: str, title: str) -> None:
        start: str = os.path.dirname(path)

        def dump_item(item: Nameserver) -> str:
            address: str = item.info.ip_address
            relpath: str = os.path.relpath(item.path, start)
            rellink: str = os.path.join(relpath, "readme.md")
            return f"* [{address}]({rellink}): {item.info.reliability}"

        def dump_reliability(title: str, value: List[Nameserver]) -> str:
            lines: List[str] = list()
            for item in sorted(value, key=lambda i: i.info.reliability,
                               reverse=True):
                lines.append(dump_item(item))
            text: str = "\n".join(lines)
            return f"### {title}\n{text}"

        def dump_group(title: str, value: Dict[int, List[Nameserver]]) -> str:
            prefix: str = f"{title.lower()}-score"
            scores: List[str] = [f"[{r}](#{prefix}-{r})" for r in value.keys()]
            lines: List[str] = [f"All scores for {title}: {', '.join(scores)}"]
            for r, m in sorted(value.items(), key=lambda v: v[0],
                               reverse=True):
                lines.append(dump_reliability(f"{title} score {r}", m))
            return "\n\n".join(lines) if len(lines) > 1 else "No nameserver"

        def dump_text() -> str:
            ipv4: Dict[int, List[Nameserver]] = {i: list() for i in range(11)}
            ipv6: Dict[int, List[Nameserver]] = {i: list() for i in range(11)}

            for item in sorted(self, key=lambda item: item.info.ip_address):
                address: str = item.info.ip_address
                reliability: int = int(item.info.reliability * 10)
                if self.is_ipv4(address):
                    ipv4[reliability].append(item)
                elif self.is_ipv6(address):
                    ipv6[reliability].append(item)

            for n in range(1, 11):
                if len(ipv4[n]) <= 0:
                    del ipv4[n]
                if len(ipv6[n]) <= 0:
                    del ipv6[n]
            del ipv4[0]
            del ipv6[0]

            return f"""# {title}

List of all [IPv4](#ipv4) and [IPv6](#ipv6) nameservers.

## IPv4

{dump_group("IPv4", ipv4)}

## IPv6

{dump_group("IPv6", ipv6)}
"""

        with open(path, "w") as whdl:
            whdl.write(dump_text())


class Subsets(Generic[LT]):

    class Subset(NameserverSet):
        def __init__(self, label: LT):
            self.__title: str = str(label)
            self.__label: LT = label
            super().__init__()

        @property
        def title(self) -> str:
            return self.__title

        @property
        def label(self) -> LT:
            return self.__label

        def dump(self, path: str) -> None:
            super().dump(os.path.join(path, f"{self.title}.md"), self.title)

    def __init__(self):
        self.__subs: Dict[LT, Subsets.Subset] = dict()

    def __iter__(self) -> Iterator[Subset]:
        return iter(self.__subs.values())

    def __getitem__(self, key: LT) -> Subset:
        if key not in self.__subs:
            self.__subs[key] = self.Subset(key)
        return self.__subs[key]

    def dump(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)
        assert os.path.isdir(path)
        for sub in sorted(self, key=lambda sub: sub.title):
            if sub.label:
                sub.dump(path)


class CountrySet(Subsets[str]):

    def __init__(self):
        super().__init__()

    def add(self, item: Nameserver):
        self[item.info.country_code].add(item)


class Resources(NameserverSet):

    DATADIR = "resources"
    NAMEDIR = "nameservers"

    def __init__(self, basedir: str, project: str):
        self.__countries: CountrySet = CountrySet()
        self.__basedir: str = basedir
        self.__project: str = project
        super().__init__()

    @property
    def datadir(self) -> str:
        return os.path.join(self.__basedir, self.DATADIR, self.__project)

    @property
    def namedir(self) -> str:
        return os.path.join(self.__basedir, self.NAMEDIR, self.__project)

    def add(self, item: dnsprobe_nameservers.item):
        path: str = os.path.join(self.namedir, item.ip_address)
        nameserver: Nameserver = Nameserver.load(path, item)
        self.__countries.add(nameserver)
        super().add(nameserver)

    def dump(self) -> None:
        title: str = "nameservers"
        super().dump(os.path.join(self.datadir, f"{title}.md"), title)
        self.__countries.dump(os.path.join(self.datadir, "countries"))
        for item in sorted(self, key=lambda item: item.info.ip_address):
            item.dump()

    @classmethod
    def load(cls, basedir: str, project: str, csvfile: str) -> "Resources":
        resources = Resources(basedir, project)
        nameservers = dnsprobe_nameservers(resources.datadir, csvfile)
        for addr in nameservers:
            resources.add(nameservers[addr])
        return resources


Resources.load(BASEDIR, "public-dns", "nameservers-all.csv").dump()
