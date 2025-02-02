import json
from pathlib import Path
import re
import click
import pymupdf

from logger import logger
from models import Stats, Config


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
            return [choice["name"] for choice in choices["teams"]]
    except FileNotFoundError:
        logger.error("ファイル %s が見つかりません。", file_path)
        return []


def get_yards(
    pdf_document: pymupdf.Document, team_name_list: list[str], is_run: bool
) -> dict:
    """
    Extracts and returns the run or pass yards for two teams from a PDF document.
    Args:
        pdf_document (pymupdf.Document): The PDF document to be analyzed.
        team_a (str): The name of the first team.
        team_b (str): The name of the second team.
        is_run (bool): If True, search for run yards; if False, search for pass yards.
    Returns:
        dict: A dictionary with team names as keys and lists of extracted yard values as values.
    """
    # 正規表現パターンを作成
    if is_run:
        search_format = re.compile(r"-?\d+yラン")
        parse_keyword = "yラン"
    else:
        search_format = re.compile(r"-?\d+yパス")
        parse_keyword = "yパス"
    # 全ページをループして特定の書式のテキストを抽出
    extracted_text_dict_list = [{"name": "", "texts": []}, {"name": "", "texts": []}]

    team_list_in_file = []

    #  チーム名の出現数カウント
    team_a_count = 0
    team_b_count = 0

    team_mode = 0

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text("text")
        units = text.split("\n")
        for unit in units:
            # 「チーム名 Time」の記法からチーム名を抽出
            if (
                unit.split(" ")[0] in team_name_list
                and unit.split(" ")[0] not in team_list_in_file
            ):
                team_list_in_file.append(unit.split(" ")[0])
            # チーム名が見つかったら、その後の記録をそのチームのものとして処理
            if unit.split(" ")[0] in team_list_in_file:
                if unit.split(" ")[0] == team_list_in_file[0]:
                    team_mode = 0
                    team_a_count += 1
                else:
                    team_mode = 1
                    team_b_count += 1
            matches = search_format.findall(unit)
            if matches:
                extracted_text_dict_list[team_mode]["texts"].append(
                    int(matches[0].split(parse_keyword)[0])
                )
    if team_a_count == 0 or team_b_count == 0:
        logger.error("チームが一つしか見つかりません")
    extracted_text_dict_list[0]["name"] = team_list_in_file[0]
    extracted_text_dict_list[1]["name"] = team_list_in_file[1]
    return extracted_text_dict_list

@click.command()
@click.argument("pdf_path", type=Path)
@click.option("--config", type=Path, default="config.json")
def main(pdf_path: Path, config: Path):
    config = load_config_from_file("config.json")
    team_names_list = load_team_names_from_file("teams.json")
    pdf_document = open_pdf(pdf_path)
    run_yards_dict_list = get_yards(pdf_document, team_names_list, True)
    pass_yards_dict_list = get_yards(pdf_document, team_names_list, False)
    for index in range(2):
        stats = Stats(
            run_yards=run_yards_dict_list[index]["texts"],
            pass_yards=pass_yards_dict_list[index]["texts"],
        )
        logger.info(
            "%s had %d runs greater than 15 yards.",
            run_yards_dict_list[index]['name'],
            stats.count_large_run_yards(config.run_long_gain_threshold),
        )
        logger.info(
            "%s had %d passes greater than 20 yards.",
            pass_yards_dict_list[index]['name'],
            stats.count_large_pass_yards(config.pass_long_gain_threshold),
        )


if __name__ == "__main__":
    main()
