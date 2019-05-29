#!/bin/sh -ex

for uid in r6kb-f76c hr5e-pz98 mjei-r6sw v9d4-guqe gzvu-8hu2 2u5d-29ty 5mfa-483b nuea-zwfy ahe3-c3ze qapr-gczi kvdp-n329 9jrk-izbx t4sj-uv2s eay6-uaqx yrhu-vpfh; do
    for format in KML KMZ Shapefile Original GeoJSON; do
        mkdir -p "raw-gis-${format}"
        filename="raw-gis-${format}/${uid}"
        if test -e "${filename}"; then
            echo "${filename} already exists"
        else
            wget "https://data.code4sa.org/api/geospatial/${uid}?method=export&format=${format}" -O "${filename}"
        fi
    done
done
