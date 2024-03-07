# !/usr/bin/env bash

echo "PWD: ${PWD}"
echo "PATH: ${PATH}"
echo "SHELL: ${SHELL}"

DATADIR=$(dirname $(dirname $0))/resources/public-dns
echo "save all resources to dir: ${DATADIR}"

wget -P ${DATADIR} --page-requisites --no-host-directories "https://public-dns.info/nameservers-all.csv"
wget -P ${DATADIR} --page-requisites --no-host-directories "https://public-dns.info/nameservers-all.txt"
wget -P ${DATADIR} --page-requisites --no-host-directories "https://public-dns.info/nameservers.csv"
wget -P ${DATADIR} --page-requisites --no-host-directories "https://public-dns.info/nameservers.txt"

git add ${DATADIR} && git commit --message="sync from public-dns.info $(date '+%F %T')"
