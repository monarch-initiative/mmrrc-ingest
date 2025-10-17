"""
Transform for MMRRC genotype-to-phenotype associations.

Reads preprocessed genotype_to_phenotype.csv and creates GenotypeToPhenotypicFeatureAssociation edges.
"""

import uuid
from typing import Any, Optional

import koza
from koza import KozaTransform
from biolink_model.datamodel.pydanticmodel_v2 import GenotypeToPhenotypicFeatureAssociation


@koza.transform_record()
def transform_record(koza_transform: KozaTransform, row: dict[str, Any]) -> list[GenotypeToPhenotypicFeatureAssociation]:
    """
    Transform a genotype-phenotype row into a GenotypeToPhenotypicFeatureAssociation.

    Args:
        koza_transform: Koza transform context
        row: Dictionary containing genotype-phenotype data from genotype_to_phenotype.csv

    Returns:
        list[GenotypeToPhenotypicFeatureAssociation]: A list containing a biolink association
    """
    # Skip rows without required IDs
    if not row.get('strain_id') or not row.get('phenotype_id'):
        return []

    # Skip rows with empty phenotype labels (failed extraction)
    if not row.get('phenotype_label') or row['phenotype_label'].strip() == '':
        return []

    association = GenotypeToPhenotypicFeatureAssociation(
        id=f"uuid:{uuid.uuid4()}",
        subject=row['strain_id'],
        predicate='biolink:has_phenotype',
        object=row['phenotype_id'],
        aggregator_knowledge_source=['infores:monarchinitiative'],
        primary_knowledge_source='infores:mmrrc',
        knowledge_level='knowledge_assertion',
        agent_type='manual_agent'
    )

    return [association]
