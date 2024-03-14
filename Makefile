MAKEFLAGS += --always-make

update-databases:
	dnsprobe export-databases --output ./databases public-dns && python3 ./scripts/build-public-dns.info.py init
	git add databases/ nameservers/ && git commit --message="update databases $$(date '+%F %T')"

build-nameservers:
	python3 ./scripts/build-public-dns.info.py dump
	git add nameservers/ && git commit --message="build databases $$(date '+%F %T')"

sync-public-dns:
	bash ./scripts/sync-from-public-dns.info.sh
