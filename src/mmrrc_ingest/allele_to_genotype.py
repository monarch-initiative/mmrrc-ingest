"""
Transform for MMRRC allele-to-genotype associations.

Reads preprocessed allele_to_genotype.csv and creates GenotypeToVariantAssociation edges.
"""

import uuid
from typing import Any

import koza
from biolink_model.datamodel.pydanticmodel_v2 import GenotypeToVariantAssociation
from koza import KozaTransform


@koza.transform_record()
def transform_record(koza_transform: KozaTransform, row: dict[str, Any]) -> list[GenotypeToVariantAssociation]:
    """
    Transform an allele-genotype row into a GenotypeToVariantAssociation.

    Args:
        koza_transform: Koza transform context
        row: Dictionary containing allele-genotype data from allele_to_genotype.csv

    Returns:
        list[GenotypeToVariantAssociation]: A list containing a biolink association

    """
    # Skip rows without required IDs
    if not row.get("allele_id") or not row.get("strain_id"):
        return []

    association = GenotypeToVariantAssociation(
        id=f"uuid:{uuid.uuid4()}",
        subject=row["strain_id"],
        predicate="biolink:has_sequence_variant",
        object=row["allele_id"],
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:mmrrc",
        knowledge_level="knowledge_assertion",
        agent_type="manual_agent",
    )

    return [association]
