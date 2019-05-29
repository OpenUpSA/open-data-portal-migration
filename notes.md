The datasets to be ported:

* <https://data.code4sa.org/dataset/Asset-Inventory/iank-udt7>

Datahub:

* <https://datahub.io/docs/getting-started/installing-data>
* <https://datahub.io/docs/getting-started/publishing-data>


## Observations

On asset inventory:

* CSV/JSON downloads are unavailable for datasets that are:
  * Private
  * type GIS map
  * type file

* Datasets we probably want to exclude:
  * Private
  * Derived filter, charts
  * Snapshots


## Downloading

Type `dataset` (tabular):

* https://data.code4sa.org/resource/${uid}.csv
* https://data.code4sa.org/resource/${uid}.json

Type `file`:

* https://data.code4sa.org/download/${uid}/${content_type}

(where `content_type` is a MIME content type, percent-encoded,
and must match to not 404?)

Type `gis map`:

* https://data.code4sa.org/api/geospatial/${uid}?method=export&format=${format}

where `format` can be:

* KML
* KMZ
* Shapefile
* Original
* GeoJSON

Or (requires login):

* https://data.code4sa.org/api/views/${uid}/rows.csv?accessType=DOWNLOAD
* https://data.code4sa.org/api/views/${uid}/rows.json?accessType=DOWNLOAD


## Uploading to datahub.io

The `process_inventory.py` script produces data packages that that
should be compatible with CKAN / [datahub.io](https://datahub.io/).

See discussion in https://gitter.im/datahubio/chat (circa 28 May 2019).
