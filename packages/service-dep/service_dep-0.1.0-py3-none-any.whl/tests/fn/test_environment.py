"""Test fn environment."""

from service import Environment, fn


def test_fn_environment(monkeypatch):
    """Test fn environment."""

    assert fn.environment() == Environment('unknown')

    env_key = 'ENVIRONMENT'

    for case in (
        'develop',
        'testing',
        'pre-stage',
        'stage',
        'pre-production',
        'production',
    ):
        monkeypatch.setenv(env_key, case)
        assert fn.environment() == Environment(case)
