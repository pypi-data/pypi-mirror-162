"""Test for aanalyze_contextcapture.py."""

# pylint: disable=import-error
import pytest


@pytest.fixture()
def workspace_path():
    """Get the default information."""
    return r"G:\workspace"


def test_workspace(dayan_cc, workspace_path, expected_result):
    """Test task_info_iterater, we can get a expected result."""
    data = dayan_cc.check_workspace(workspace_path)
    assert data == expected_result
