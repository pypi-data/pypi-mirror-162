"""Test extends."""

from service.ext.testing import (
    money_amount,
    any_int,
    any_int_pos,
    any_int_neg,
    any_bool,
    any_url,
    any_image_url,
    any_sentence,
    any_word,
    country_name,
    currency_name,
    currency_code,
)


def test_ext_testing_builtins():
    """Test ext testing builtins."""

    assert 0 < money_amount() < 99999.9
    assert 0 <= any_int() <= 100
    assert 1 <= any_int_pos() >= 1
    assert 0 > any_int_neg() <= 0
    assert any_bool() in (True, False)
    assert 'http' in any_image_url()
    assert 'http' in any_url()
    assert len(any_word()) < len(any_sentence())
    assert isinstance(currency_code(), str) and len(currency_code()) == 3
    assert isinstance(currency_name(), str) and len(country_name()) > 1
    assert isinstance(country_name(), str) and len(country_name()) > 1
