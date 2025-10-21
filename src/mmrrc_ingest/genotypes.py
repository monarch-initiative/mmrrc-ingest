"""
Transform for MMRRC genotype nodes.

Reads preprocessed genotypes.csv and creates Genotype nodes.
"""

from typing import Any

import koza
from biolink_model.datamodel.pydanticmodel_v2 import Genotype
from koza import KozaTransform


@koza.transform_record()
def transform_record(koza_transform: KozaTransform, row: dict[str, Any]) -> list[Genotype]:
    """
    Transform a genotype row into a Genotype node.

    Args:
        koza_transform: Koza transform context
        row: Dictionary containing genotype data from genotypes.csv

    Returns:
        list[Genotype]: A list containing a biolink Genotype node

    """
    # Skip rows without a strain ID
    if not row.get("strain_id"):
        return []

    genotype = Genotype(
        id=row["strain_id"],  # Already in format MMRRC:XXXXXX-XXX
        name=row["strain_designation"],
        xref=[row["other_names"]] if row.get("other_names") else None,
        in_taxon=["NCBITaxon:10090"],  # All MMRRC strains are Mus musculus
        in_taxon_label="Mus musculus",
        provided_by=["infores:mmrrc"],
    )

    return [genotype]
