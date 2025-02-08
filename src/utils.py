import json
from pathlib import Path

import pymupdf  # type: ignore

from logger import logger
from models import Config


def open_pdf(file_path: Path) -> pymupdf.Document:
    """
    Opens a PDF file and returns a pymupdf.Pdf object.

    Args:
        file_path (Path): The path to the PDF file to be opened.

    Returns:
        pymupdf.Pdf: The opened PDF file as a pymupdf.Pdf object.
    """
    pdf_document = pymupdf.open(file_path)
    return pdf_document


def load_config_from_file(file_path: Path) -> Config:
    """
    Loads a configuration from a JSON file and returns a Config object.

    Args:
        file_path (Path): The path to the JSON file to be loaded.

    Returns:
        Config: The configuration as a Config object.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        config_dict = json.load(f)
        return Config(**config_dict)


def load_team_names_from_file(file_path):
    """
    ファイルから選択肢を読み込む
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            choices = json.load(f)
            team_names = [choice["name"] for choice in choices["teams"]]
            team_abbreviation = choices["abbreviation"]
            return team_names, team_abbreviation
    except FileNotFoundError as exc:
        logger.error("ファイル %s が見つかりません。", file_path)
        raise FileNotFoundError from exc
