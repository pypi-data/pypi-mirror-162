"""The plugin of the pytest.

The pytest plugin hooks do not need to be imported into any test code, it will
load automatically when running pytest.
"""

# pylint: disable=import-error
import pytest

from dayan_contextcapture.analyze_contextcapture import AnalyzeContextCapture


@pytest.fixture()
def expected_result():
    """Get the expected_result information."""
    return r"G:\workspace"


@pytest.fixture()
def analyze_info():
    """Get user info."""
    return {
        "cg_file": r"G:\workspace",
        "workspace": r"G:\workspace",
        "project_name": "Project1"
    }


@pytest.fixture()
def dayan_cc(analyze_info):
    """Create an cc object."""
    return AnalyzeContextCapture(**analyze_info)
