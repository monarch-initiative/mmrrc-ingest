"""
Test file for MMRRC genotype-to-gene association transform.

Tests the transform of genotype-to-gene associations from preprocessed MMRRC data.
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GenotypeToGeneAssociation
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from genotype_to_gene import transform_record


@pytest.fixture
def genotype_gene_row() -> dict[str, str]:
    """Example genotype-to-gene row from genotype_to_gene.csv"""
    return {
        "strain_id": "MMRRC:000001-UNC",
        "gene_id": "MGI:95526",
        "gene_symbol": "Fgg",
        "gene_name": "fibrinogen gamma chain",
        "pubmed_ids": "PMID:11521996|PMID:15096455",
    }


@pytest.fixture
def genotype_gene_association(genotype_gene_row: dict[str, str]) -> GenotypeToGeneAssociation:
    """Transform a genotype-to-gene row"""
    koza_transform = KozaTransform(mappings={}, writer=PassthroughWriter(), extra_fields={})
    result = transform_record(koza_transform, genotype_gene_row)
    return result[0] if result else None


def test_association_subject(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test association subject is the genotype ID"""
    assert genotype_gene_association.subject == "MMRRC:000001-UNC"


def test_association_predicate(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test association predicate is related_to"""
    assert genotype_gene_association.predicate == "biolink:related_to"


def test_association_object(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test association object is the gene ID"""
    assert genotype_gene_association.object == "MGI:95526"


def test_association_publications(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test strain-level PubMed IDs are attached as publications"""
    assert genotype_gene_association.publications == ["PMID:11521996", "PMID:15096455"]


def test_association_knowledge_source(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test association knowledge sources"""
    assert genotype_gene_association.primary_knowledge_source == "infores:mmrrc"
    assert "infores:monarchinitiative" in genotype_gene_association.aggregator_knowledge_source


def test_association_knowledge_level(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test association knowledge level"""
    assert genotype_gene_association.knowledge_level == "knowledge_assertion"


def test_association_agent_type(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test association agent type"""
    assert genotype_gene_association.agent_type == "manual_agent"


def test_association_category(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test association has correct biolink category"""
    assert "biolink:GenotypeToGeneAssociation" in genotype_gene_association.category


def test_association_has_id(genotype_gene_association: GenotypeToGeneAssociation) -> None:
    """Test association has a generated ID"""
    assert genotype_gene_association.id is not None
    assert genotype_gene_association.id.startswith("uuid:")


def test_missing_gene_id_skipped() -> None:
    """Test rows without a gene ID produce no association"""
    koza_transform = KozaTransform(mappings={}, writer=PassthroughWriter(), extra_fields={})
    row = {"strain_id": "MMRRC:000001-UNC", "gene_id": "", "pubmed_ids": ""}
    assert transform_record(koza_transform, row) == []


def test_no_publications_when_absent() -> None:
    """Test publications is None when the strain has no PubMed IDs"""
    koza_transform = KozaTransform(mappings={}, writer=PassthroughWriter(), extra_fields={})
    row = {"strain_id": "MMRRC:000001-UNC", "gene_id": "MGI:95526", "pubmed_ids": None}
    association = transform_record(koza_transform, row)[0]
    assert association.publications == [] or association.publications is None
