"""Testing ext funcs."""

import random

from faker import Faker
from service.fn import load_locales

from httpx import AsyncClient as XClient
from fastapi.testclient import TestClient as ApiClient
from starlette.testclient import TestClient as AppClient

Faker.seed(random.randint(0, 99999))

safe_faker: Faker = Faker(locale=('en_US', ))
i18n_faker: Faker = Faker(locale=load_locales())


def shake():
    """Shake faker seed."""
    Faker.seed(random.randint(0, 100))


def country_name(lang: str = None) -> str:
    """Gen country name."""
    faker = i18n_faker if lang else safe_faker
    shake()
    if lang:
        faker.setLocale(lang)
    return str(faker.country())


def currency_name(lang: str = None) -> str:
    """Gen currency name like `Russian Ruble`."""
    faker = i18n_faker if lang else safe_faker
    shake()
    if lang:
        faker.setLocale(lang)
    return str(faker.currency_name())


def currency_code(lang: str = None) -> str:
    """Gen currency code like `USD` or `RUB`."""
    faker = i18n_faker if lang else safe_faker
    shake()
    if lang:
        faker.setLocale(lang)
    return str(faker.currency_code())


def any_word(lang: str = None) -> str:
    """Any word."""
    faker = i18n_faker if lang else safe_faker
    shake()
    if lang:
        faker.setLocale(lang)
    return str(faker.word())


def money_amount(min_amount: float = 0, max_amount: float = 99999.99) -> float:
    """Gen money amount."""
    return round(random.uniform(min_amount, max_amount), ndigits=2)


def any_sentence(lang: str = None) -> str:
    """Any sentence."""
    faker = i18n_faker if lang else safe_faker
    shake()
    if lang:
        faker.setLocale(lang)
    return str(faker.sentence())


def any_bool() -> bool:
    """Any bool."""
    return random.choice([True, False])


def any_url() -> str:
    """Any url."""
    return i18n_faker.url()


def any_image_url() -> str:
    """Any image url."""
    shake()
    return i18n_faker.image_url()


def any_int(range_start: int = 0, range_end: int = 100) -> int:
    """Any int from range."""
    return random.randint(range_start, range_end)


def any_int_pos() -> int:
    """Any int positive."""
    return any_int(range_start=1, range_end=100)  # noqa


def any_int_neg() -> int:
    """Any int negative."""
    return any_int(range_start=-100, range_end=-1)


__all__ = (
    'ApiClient',
    'AppClient',
    'XClient',
    'any_int',
    'any_url',
    'any_word',
    'any_bool',
    'any_sentence',
    'any_int_pos',
    'any_int_neg',
    'any_image_url',
    'country_name',
    'currency_name',
    'currency_code',
    'money_amount',
    'safe_faker',
    'i18n_faker',
)
