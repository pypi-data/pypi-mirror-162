"""Test load settings with different execution environment."""

import os

import json
import shutil

from pathlib import Path
from pytest import fixture

from service import fn


@fixture
def translations() -> None:
    """Mock translations in temporary dir."""

    paths = fn.paths()

    path_en = Path(paths.i18n / 'en.json')
    path_ru = Path(paths.i18n / 'ru.json')

    paths.i18n.mkdir(parents=True, exist_ok=True)

    with open(path_en.as_posix(), 'w') as outfile:
        outfile.write(
            json.dumps(
                {
                    'foo': 'Foo',
                    'bar': 'Bar',
                    'fizz': {
                        'zero': 'You do not have any fizzes.',
                        'one': 'You have one fizz.',
                        'many': 'You have %{count} fizzes.',
                    }
                },
                ensure_ascii=False,
                indent=4,
            ),
        )

    with open(path_ru.as_posix(), 'w') as outfile:
        outfile.write(
            json.dumps(
                {
                    "foo": "Фу",
                    "bar": "Бар",
                    'fizz': {
                        'zero': 'У вас нет ни одного физа.',
                        'one': 'У вас есть один физ.',
                        'many': 'У вас есть %{count} физов.',
                    }
                },
                ensure_ascii=False,
                indent=4,
            ),
        )

    yield

    shutil.rmtree(paths.assets.as_posix(), ignore_errors=True)


async def test_i18n_translations(
    translations,    # noqa
    env,    # noqa
    pyproject,    # noqa
    app: fn.Service,
):
    """Test i18n static translations."""
    assert app.spec.version == '0.1.0'

    i18n = app._  # noqa
    assert 'Foo' == i18n('foo')
    assert 'Bar' == i18n('bar')

    assert 'You do not have any fizzes.' == i18n('fizz', count=0)
    assert 'You have one fizz.' == i18n('fizz', count=1)
    assert 'You have 5 fizzes.' == i18n('fizz', count=5)

    assert 'Фу' == i18n('foo', locale='ru')
    assert 'Бар' == i18n('bar', locale='ru')

    assert 'У вас нет ни одного физа.' == i18n('fizz', count=0, locale='ru')
    assert 'У вас есть один физ.' == i18n('fizz', count=1, locale='ru')
    assert 'У вас есть 5 физов.' == i18n('fizz', count=5, locale='ru')
