"""
Test file for MMRRC genotype-to-phenotype association transform.

Tests the transform of genotype-to-phenotype associations from preprocessed MMRRC data.
"""

import pytest
from koza import KozaTransform
from biolink_model.datamodel.pydanticmodel_v2 import GenotypeToPhenotypicFeatureAssociation
from koza.io.writer.passthrough_writer import PassthroughWriter

from mmrrc_ingest.genotype_to_phenotype import transform_record


@pytest.fixture
def genotype_phenotype_row() -> dict[str, str]:
    """Example genotype-to-phenotype row from genotype_to_phenotype.csv"""
    return {
        'strain_id': 'MMRRC:000002-UNC',
        'phenotype_id': 'MP:0000063',
        'phenotype_label': 'decreased bone mineral density'
    }


@pytest.fixture
def genotype_phenotype_association(genotype_phenotype_row: dict[str, str]) -> GenotypeToPhenotypicFeatureAssociation:
    """Transform a genotype-to-phenotype row"""
    koza_transform = KozaTransform(
        mappings={},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    result = transform_record(koza_transform, genotype_phenotype_row)  # type: ignore
    return result[0] if result else None  # type: ignore


def test_association_subject(genotype_phenotype_association: GenotypeToPhenotypicFeatureAssociation) -> None:
    """Test association subject is the genotype ID"""
    assert genotype_phenotype_association.subject == 'MMRRC:000002-UNC'


def test_association_predicate(genotype_phenotype_association: GenotypeToPhenotypicFeatureAssociation) -> None:
    """Test association predicate is has_phenotype"""
    assert genotype_phenotype_association.predicate == 'biolink:has_phenotype'


def test_association_object(genotype_phenotype_association: GenotypeToPhenotypicFeatureAssociation) -> None:
    """Test association object is the phenotype ID"""
    assert genotype_phenotype_association.object == 'MP:0000063'


def test_association_knowledge_source(genotype_phenotype_association: GenotypeToPhenotypicFeatureAssociation) -> None:
    """Test association knowledge sources"""
    assert genotype_phenotype_association.primary_knowledge_source == 'infores:mmrrc'
    assert 'infores:monarchinitiative' in genotype_phenotype_association.aggregator_knowledge_source


def test_association_knowledge_level(genotype_phenotype_association: GenotypeToPhenotypicFeatureAssociation) -> None:
    """Test association knowledge level"""
    assert genotype_phenotype_association.knowledge_level == 'knowledge_assertion'


def test_association_agent_type(genotype_phenotype_association: GenotypeToPhenotypicFeatureAssociation) -> None:
    """Test association agent type"""
    assert genotype_phenotype_association.agent_type == 'manual_agent'


def test_association_has_id(genotype_phenotype_association: GenotypeToPhenotypicFeatureAssociation) -> None:
    """Test association has a generated ID"""
    assert genotype_phenotype_association.id is not None
    assert genotype_phenotype_association.id.startswith('uuid:')


def test_association_category(genotype_phenotype_association: GenotypeToPhenotypicFeatureAssociation) -> None:
    """Test association has correct biolink category"""
    assert 'biolink:GenotypeToPhenotypicFeatureAssociation' in genotype_phenotype_association.category
