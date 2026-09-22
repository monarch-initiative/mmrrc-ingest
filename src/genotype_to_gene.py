"""
Transform for MMRRC genotype-to-gene associations.

Reads preprocessed genotype_to_gene.csv and creates GenotypeToGeneAssociation edges.

MMRRC identifies most strains by their target gene (MGI gene accession) rather
than by an allele accession, so this connects the large gene-trap/targeted set
that carries no allele accession. Following the Alliance convention, the
predicate is left deliberately vague (`biolink:related_to`).
"""

from typing import Any

import koza
from biolink_model.datamodel.pydanticmodel_v2 import GenotypeToGeneAssociation
from koza import KozaTransform


@koza.transform_record()
def transform_record(koza_transform: KozaTransform, row: dict[str, Any]) -> list[GenotypeToGeneAssociation]:
    """
    Transform a genotype-gene row into a GenotypeToGeneAssociation.

    Args:
        koza_transform: Koza transform context
        row: Dictionary containing genotype-gene data from genotype_to_gene.csv

    Returns:
        list[GenotypeToGeneAssociation]: A list containing a biolink association

    """
    # Skip rows without required IDs
    if not row.get("strain_id") or not row.get("gene_id"):
        return []

    predicate = "biolink:related_to"

    # Strain-level PubMed references, pipe-delimited in the preprocessed CSV.
    publications = row["pubmed_ids"].split("|") if row.get("pubmed_ids") else None

    association = GenotypeToGeneAssociation(
        subject=row["strain_id"],
        predicate=predicate,
        object=row["gene_id"],
        publications=publications,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:mmrrc",
        knowledge_level="knowledge_assertion",
        agent_type="manual_agent",
    )

    return [association]
