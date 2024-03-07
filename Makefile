MAKEFLAGS += --always-make

update-databases:
	dnsprobe export-databases --output ./databases public-dns

sync:
	bash ./scripts/sync-from-public-dns.info.sh
