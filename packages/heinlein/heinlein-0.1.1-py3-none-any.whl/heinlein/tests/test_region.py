import pytest
from heinlein import Region
import astropy.units as u

@pytest.fixture
def circular_region():
    return Region(center=(5,5), radius = 5*u.degree)

@pytest.fixture
def polygon_region():
    return 5


def test_region_within(circular_region):
    new_region = Region(center=(4,4), radius = 1*u.degree)
    assert circular_region.contains(new_region)


def test_over_edge_detection():
    new_region = Region([(1,-89), (1, 89), (359, 89), (359, -89)])
    assert new_region._edge_overlap == (True, True)
