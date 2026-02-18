import pytest

from tests.factories import CartFactory, CategoryFactory, ProductFactory


@pytest.fixture
def category(db):
    return CategoryFactory()


@pytest.fixture
def product(db):
    return ProductFactory()


@pytest.fixture
def cart(db):
    return CartFactory()
