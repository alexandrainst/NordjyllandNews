"""Session-wide fixtures for tests."""

from typing import Generator

import pytest
from hydra import compose, initialize

# Initialise Hydra
initialize(config_path="../config", version_base=None)


@pytest.fixture(scope="session")
def config():
    return compose(
        config_name="config",
        overrides=["testing=True"],
    )


@pytest.fixture(scope="session")
def page() -> Generator[int, None, None]:
    yield 1
