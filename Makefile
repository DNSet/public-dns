MAKEFLAGS += --always-make

update-databases:
	dnsprobe export-databases --output ./databases public-dns

build-databases:
	python3 ./scripts/build-public-dns.info.py
	git add nameservers/ resources/ && git commit --message="build databases $$(date '+%F %T')"

sync:
	bash ./scripts/sync-from-public-dns.info.sh
