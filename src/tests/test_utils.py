from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import pytest
from utils import open_pdf, load_config_from_file, load_team_names_from_file
from models import Config


@patch("utils.pymupdf.open")
def test_open_pdf(mock_pymupdf_open):
    mock_pdf = MagicMock()
    mock_pymupdf_open.return_value = mock_pdf

    file_path = Path("/path/to/test.pdf")
    result = open_pdf(file_path)

    mock_pymupdf_open.assert_called_once_with(file_path)
    assert result == mock_pdf


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"run_long_gain_threshold":10, "pass_long_gain_threshold":20}',
)
@patch("utils.Config")
def test_load_config_from_file(mock_config, mock_file):
    mock_config.return_value = Config(
        run_long_gain_threshold=10, pass_long_gain_threshold=20
    )

    file_path = Path("/path/to/config.json")
    result = load_config_from_file(file_path)

    mock_file.assert_called_once_with(file_path, "r", encoding="utf-8")
    mock_config.assert_called_once_with(
        run_long_gain_threshold=10, pass_long_gain_threshold=20
    )
    assert result.run_long_gain_threshold == 10
    assert result.pass_long_gain_threshold == 20


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"teams": [{"name": "Team A"}, {"name": "Team B"}]}',
)
def test_load_team_names_from_file(mock_file):
    file_path = Path("/path/to/teams.json")
    result = load_team_names_from_file(file_path)

    mock_file.assert_called_once_with(file_path, "r", encoding="utf-8")
    assert result == ["Team A", "Team B"]


@patch("utils.logger.error")
def test_load_team_names_from_file_file_not_found(mock_logger):
    file_path = Path("/path/to/nonexistent.json")
    result = load_team_names_from_file(file_path)

    mock_logger.assert_called_once_with("ファイル %s が見つかりません。", file_path)
    assert result == []


if __name__ == "__main__":
    pytest.main()
