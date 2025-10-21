"""
Test file for MMRRC allele-to-genotype association transform.

Tests the transform of allele-to-genotype associations from preprocessed MMRRC data.
"""

import pytest
from koza import KozaTransform
from biolink_model.datamodel.pydanticmodel_v2 import GenotypeToVariantAssociation
from koza.io.writer.passthrough_writer import PassthroughWriter

from mmrrc_ingest.allele_to_genotype import transform_record


@pytest.fixture
def allele_genotype_row() -> dict[str, str]:
    """Example allele-to-genotype row from allele_to_genotype.csv"""
    return {
        'allele_id': 'MGI:3696864',
        'allele_symbol': 'Tg(Fga,Fgb,Fgg)1Unc',
        'allele_name': 'transgene insertion 1, University of North Carolina',
        'strain_id': 'MMRRC:000001-UNC',
        'mutation_type': 'TG',
        'chromosome': 'unknown'
    }


@pytest.fixture
def allele_genotype_association(allele_genotype_row: dict[str, str]) -> GenotypeToVariantAssociation:
    """Transform an allele-to-genotype row"""
    koza_transform = KozaTransform(
        mappings={},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    result = transform_record(koza_transform, allele_genotype_row)
    return result[0] if result else None


def test_association_subject(allele_genotype_association: GenotypeToVariantAssociation) -> None:
    """Test association subject is the genotype ID"""
    assert allele_genotype_association.subject == 'MMRRC:000001-UNC'


def test_association_predicate(allele_genotype_association: GenotypeToVariantAssociation) -> None:
    """Test association predicate is has_sequence_variant"""
    assert allele_genotype_association.predicate == 'biolink:has_sequence_variant'


def test_association_object(allele_genotype_association: GenotypeToVariantAssociation) -> None:
    """Test association object is the allele ID"""
    assert allele_genotype_association.object == 'MGI:3696864'


def test_association_knowledge_source(allele_genotype_association: GenotypeToVariantAssociation) -> None:
    """Test association knowledge sources"""
    assert allele_genotype_association.primary_knowledge_source == 'infores:mmrrc'
    assert 'infores:monarchinitiative' in allele_genotype_association.aggregator_knowledge_source


def test_association_knowledge_level(allele_genotype_association: GenotypeToVariantAssociation) -> None:
    """Test association knowledge level"""
    assert allele_genotype_association.knowledge_level == 'knowledge_assertion'


def test_association_agent_type(allele_genotype_association: GenotypeToVariantAssociation) -> None:
    """Test association agent type"""
    assert allele_genotype_association.agent_type == 'manual_agent'


def test_association_has_id(allele_genotype_association: GenotypeToVariantAssociation) -> None:
    """Test association has a generated ID"""
    assert allele_genotype_association.id is not None
    assert allele_genotype_association.id.startswith('uuid:')


def test_association_category(allele_genotype_association: GenotypeToVariantAssociation) -> None:
    """Test association has correct biolink category"""
    assert 'biolink:GenotypeToVariantAssociation' in allele_genotype_association.category
