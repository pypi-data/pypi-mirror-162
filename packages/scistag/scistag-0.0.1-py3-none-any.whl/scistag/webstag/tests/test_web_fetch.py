import pytest
from scistag.webstag import web_fetch
from scistag.tests import TestConstants


def test_web_fetch():
    data = web_fetch(TestConstants.STAG_URL)
    assert data is not None
    assert len(data) == pytest.approx(TestConstants.CAR_IMAGE_SIZE, 1000)
    assert web_fetch("http://not-existing-url.abc", 0.1) is None
