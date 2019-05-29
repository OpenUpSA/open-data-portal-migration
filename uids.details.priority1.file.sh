#!/bin/sh -ex

# https://data.code4sa.org/Government/Air-Quality-Monitoring-Station-Locations-and-Pollu/v7mq-78bq
uid=v7mq-78bq; wget https://data.code4sa.org/download/${uid}/text%2Fplain -O raw-files/${uid}.saaqis-monitoring-stations.json

# https://data.code4sa.org/Government/Transport-infrastructure-in-the-Northern-Cape-Prov/jm9x-hu7d
uid=jm9x-hu7d; wget https://data.code4sa.org/download/${uid}/application%2Fzip -O raw-files/${uid}.osm_transportationnc_161118_export_gpkg.zip
