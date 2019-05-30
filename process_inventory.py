#!/usr/bin/env python
"""
Process the data.code4sa.org Socrata asset inventory in various ways.
"""
import csv
import datetime as dt
import re
from textwrap import dedent
from typing import Dict, List, Optional, Tuple

from datapackage import Package

# Expected Asset Inventory field names:
expected_fieldnames = [
    "URL",
    "U ID",
    "Public",
    "Derived View",
    "Parent UID",
    "Domain",
    "Type",
    "Name",
    "Description",
    "Visits",
    "Creation Date",
    "Last Update Date (data)",
    "Category",
    "Keywords",
    "Downloads",
    "Owner",
    "Contact Email",
    "License",
    "Publication Stage",
    "Published Version Name",
    "Published Version UID",
    "data_provided_by",
    "Publishing Department",
    "routing_approval",
    "api_endpoint",
    "source_link",
    "owner_uid",
    "View Moderation Status",
    "provenance",
]


# Predicates for asset inventory row selection:


def is_published(row: dict) -> bool:
    return (
        row["Public"] == "true"
        and row["Derived View"] == "false"
        and row["Publication Stage"] == "published"
    )


def is_dataset(row: dict) -> bool:
    return row["Type"] == "dataset"


def is_gis_map(row: dict) -> bool:
    return row["Type"] == "gis map"


def print_details(row: dict) -> None:
    uid = row["U ID"]
    public = row["Public"]
    derived = row["Derived View"]
    parent_uid = row["Parent UID"]
    type_ = row["Type"]
    name = row["Name"]
    category = row["Category"]
    publication_stage = row["Publication Stage"]
    published_version = row["Published Version UID"]
    print(
        uid,
        f"public={public:5}",
        f"derived={derived:5}",
        f"parent={parent_uid:9}",
        f"type={type_:8}",
        f"category={category:10}",
        f"stage={publication_stage:11}",
        f"published={published_version:9}",
        f"name={name}",
    )


def derive_name(row: dict) -> str:
    """
    Data package compatible names: alphanumeric only, and slugified with "-" as separator.
    """
    name: str = row["Name"]
    name = name.lower()
    name = re.sub(r"[^a-z0-9]", " ", name)
    name = "-".join(name.split())
    return name


def data_package_from_dataset(row: dict) -> Tuple[str, Package]:
    """
    Make a data package definition from a dataset row.
    """
    assert "dataset" == row["Type"], row
    uid: str = row["U ID"]

    # Initialise the data package from the CSV data.
    package = Package()
    csv_path = f"raw-csv/{uid}.csv"
    package.infer(csv_path)

    # Set a more readable name
    package.descriptor["name"] = derive_name(row)

    # Update standard descriptor fields from the row metadata.
    package.descriptor["title"] = row["Name"]
    package.descriptor["description"] = row["Description"]
    # Sources require a title: fall back to using the link for it, otherwise skip it.
    source_title: Optional[str] = (
        row["data_provided_by"]
        if row["data_provided_by"]
        else row["source_link"]
        if row["source_link"]
        else None
    )
    if source_title:
        package.descriptor["sources"] = [
            {
                "title": source_title,
                **({"path": row["source_link"]} if row["source_link"] else {}),
            }
        ]
    package.descriptor["contributors"] = [
        {
            "title": row["Owner"],
            # XXX: Ugly but compact.
            **({"email": row["Contact Email"]} if row["Contact Email"] else {}),
        }
    ]
    keywords: List[str] = row["Keywords"].split(",")
    package.descriptor["keywords"] = keywords
    # Example value: "09/22/2014 05:34:00 PM +0000"
    socrata_datetime_format = "%m/%d/%Y %H:%M:%S %p %z"
    created: dt.datetime = dt.datetime.strptime(
        row["Creation Date"], socrata_datetime_format
    )
    package.descriptor["created"] = created.isoformat()

    # XXX: Update non-standard descriptor fields from the row metadata.
    # (Prefix these with "x_" to flag non-standard status.)
    if row["License"]:
        # TODO: Use licenses field instead
        package.descriptor["x_license_name"] = row["License"]
    if row["Category"]:
        package.descriptor["x_category"] = row["Category"]

    success = package.commit()
    assert success, package.descriptor

    # Check descriptor, and return.
    descriptor: dict = package.descriptor
    assert "tabular-data-package" == descriptor["profile"], descriptor
    assert 1 == len(descriptor["resources"]), descriptor["resources"]
    [resource] = descriptor["resources"]
    assert csv_path == resource["path"], resource
    # assert False, descriptor
    assert package.valid, package.errors
    return (uid, package)


def save_data_package(package: Package) -> None:
    name: str = package.descriptor["name"]
    # Save both the whole zip, and the JSON for comparison
    package.save(f"data-packages-json/{name}.json")
    package.save(f"data-packages-zip/{name}.zip")


def main() -> None:
    # Remember seen package names and UIDs.
    seen_names_uids: Dict[str, str] = {}

    with open("Asset_Inventory-2019-05-21.csv") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == expected_fieldnames, reader.fieldnames
        for row in reader:
            if is_published(row) and is_dataset(row):
                print_details(row)
                (uid, package) = data_package_from_dataset(row)

                # Consistency: Ensure name uniqueness
                if package.descriptor["name"] in seen_names_uids:
                    # XXX: Just one layer of unique renaming, for now.
                    # (This only affects two pairs of the May 2019 data sets.)
                    package.descriptor["name"] += "-2"
                    package.commit()

                # Consistency: Check name uniqueness
                name: str = package.descriptor["name"]
                if name in seen_names_uids:
                    raise RuntimeError(
                        dedent(
                            f"""\
                            Name {name!r} (UID {uid}) already seen as UID {seen_names_uids[name]}!
                            Row: {row!r}
                            """
                        )
                    )
                seen_names_uids[name] = uid

                save_data_package(package)


if __name__ == "__main__":
    main()
