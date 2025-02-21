import json
from pathlib import Path

import pymupdf  # type: ignore

from logger import logger
from models import Config, Stats
import csv

EXCLUDE_EXPORT_KEYS = {"run_yards", "pass_yards", "config"}


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


def open_pdf_to_list(file_path: Path) -> list:
    pdf_document = pymupdf.open(file_path)
    same_line_words = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        words = page.get_text("words")
        tmp_same_line = []
        current_y0 = 0
        margin = 3
        for word in words:
            if word[1] - current_y0 < margin:
                tmp_same_line.append(word[4])
            else:
                same_line_words.append(" ".join(tmp_same_line))
                tmp_same_line = [word[4]]
                current_y0 = word[1]
    return same_line_words


def open_pdf_to_list_only_page(pdf_document: pymupdf.Document, page_num: int) -> list:
    same_line_words = []
    page = pdf_document.load_page(page_num)
    words = page.get_text("words")
    tmp_same_line = []
    current_y0 = 0
    margin = 3
    for word in words:
        if word[1] - current_y0 < margin:
            tmp_same_line.append(word[4])
        else:
            same_line_words.append(" ".join(tmp_same_line))
            tmp_same_line = [word[4]]
            current_y0 = word[1]
    return same_line_words


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
            team_abbreviation_by_team = choices["abbreviation_by_team"]
            return team_names, team_abbreviation, team_abbreviation_by_team
    except FileNotFoundError as exc:
        logger.error("ファイル %s が見つかりません。", file_path)
        raise FileNotFoundError from exc


def export_stats_to_json(stats: Stats, file_path: Path):
    """
    Exports the given Stats object to a JSON file.

    Args:
        stats (Stats): The Stats object to be exported.
        file_path (Path): The path to the JSON file to be exported.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            stats.model_dump(exclude=EXCLUDE_EXPORT_KEYS),
            f,
            ensure_ascii=False,
            indent=4,
        )


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def export_stats_to_csv(stats: Stats, file_path: Path):
    stats_dict = stats.model_dump(exclude=EXCLUDE_EXPORT_KEYS)
    flat_stats = flatten_dict(stats_dict)

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=flat_stats.keys())
        writer.writeheader()
        writer.writerow(flat_stats)


def find_page_include_word(pdf_document: pymupdf.Document, word: str):
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        words = page.get_text("words")
        for w in words:
            if word in w[4]:
                return page_num
    return -1
