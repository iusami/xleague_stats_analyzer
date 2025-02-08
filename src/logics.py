import re
import pymupdf  # type: ignore  # noqa
from pydantic import BaseModel

from logger import logger
from models import PenaltyInfo, TeamPenaltyInfo


class ExtractedYards(BaseModel):
    team_name: str
    rushing_yards: list[int]
    passing_yards: list[int]


class TeamsExtractedYards(BaseModel):
    home_team_extracted_yards: ExtractedYards
    visitor_team_extracted_yards: ExtractedYards


def get_yards(
    pdf_document: pymupdf.Document,
    team_name_list: tuple[str],
    team_abbreviation_dict: dict[str, str],
) -> tuple[TeamsExtractedYards, TeamPenaltyInfo]:
    """
    Extracts yardage statistics from a PDF document for specified teams.
    Args:
        pdf_document (pymupdf.Document): The PDF document to be analyzed.
        team_name_list (list[str]): A list of team names to search for in the document.
        is_run (bool): If True, search for running yards; if False, search for passing yards.
    Returns:
        dict: A dictionary containing the extracted yardage statistics for each team.
              The dictionary has the following structure:
              [
                  {"name": "TeamName1", "texts": [list of yardages]},
                  {"name": "TeamName2", "texts": [list of yardages]}
              ]
    Raises:
        ValueError: If the number of teams found in the document is not equal to 2.
    """
    # 全ページをループして特定の書式のテキストを抽出
    home_extracted_yards: tuple[list[int], list[int]] = ([], [])
    home_penalty_info: list[int] = [0, 0]
    visitor_extracted_yards: tuple[list[int], list[int]] = ([], [])
    visitor_penalty_info: list[int] = [0, 0]

    team_list_in_file = []

    team_mode = 0

    # 全ページのテキストを一度に取得
    all_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        all_text += page.get_text("text") + "\n"

    units = all_text.split("\n")

    # チーム名を抽出
    for unit in units:
        if (
            unit.split(" ")[0] in list(team_name_list)
            and unit.split(" ")[0] not in team_list_in_file
        ):
            team_list_in_file.append(unit.split(" ")[0])
    logger.info("team_list_in_file: %s", team_list_in_file)
    if len(team_list_in_file) != 2:
        logger.error("見つかったチーム数が2つではありません。")
        raise ValueError("The number of teams found is not equal to 2.")

    # チーム名が見つかったら、その後の記録をそのチームのものとして処理
    for unit in units:
        if unit.split(" ")[0] in team_list_in_file:
            if unit.split(" ")[0] == team_list_in_file[0]:
                team_mode = 0
            else:
                team_mode = 1

        home_extracted_yards, visitor_extracted_yards = extract_yards(
            home_extracted_yards, visitor_extracted_yards, team_mode, unit
        )
        if "+Penalty" in unit:
            home_penalty_info, visitor_penalty_info = extract_penalty_info(
                home_penalty_info,
                visitor_penalty_info,
                team_list_in_file,
                unit,
                team_abbreviation_dict,
            )

    return TeamsExtractedYards(
        home_team_extracted_yards=ExtractedYards(
            team_name=team_list_in_file[0],
            rushing_yards=home_extracted_yards[0],
            passing_yards=home_extracted_yards[1],
        ),
        visitor_team_extracted_yards=ExtractedYards(
            team_name=team_list_in_file[1],
            rushing_yards=visitor_extracted_yards[0],
            passing_yards=visitor_extracted_yards[1],
        ),
    ), TeamPenaltyInfo(
        home_team_penalty_info=PenaltyInfo(
            count=home_penalty_info[0], yards=home_penalty_info[1]
        ),
        visitor_team_penalty_info=PenaltyInfo(
            count=visitor_penalty_info[0], yards=visitor_penalty_info[1]
        ),
    )


def extract_yards(
    home_extracted_yards: tuple[list[int], list[int]],
    visitor_extracted_yards: tuple[list[int], list[int]],
    team_mode: int,
    unit: str,
) -> tuple[tuple[list[int], list[int]], tuple[list[int], list[int]]]:
    for ct, (search_format, parse_keyword) in enumerate(
        [
            (re.compile(r"-?\d+yラン"), "yラン"),
            (re.compile(r"-?\d+yパス"), "yパス"),
        ]
    ):
        # logger.info("unit: %s", unit)
        matches = search_format.findall(unit)
        if matches:
            if team_mode == 0:
                home_extracted_yards[ct].append(int(matches[0].split(parse_keyword)[0]))
            else:
                visitor_extracted_yards[ct].append(
                    int(matches[0].split(parse_keyword)[0])
                )
    return home_extracted_yards, visitor_extracted_yards


def extract_penalty_info(
    home_penalty_info,
    visitor_penalty_info,
    team_list_in_file,
    unit,
    team_abbreviation_dict,
) -> tuple[list[int], list[int]]:
    unit_parts = [part for part in unit.split(" ") if part]
    penalty_team = unit_parts[unit_parts.index("+Penalty") + 1]
    if "ディクライン" not in unit:
        penalty_yards = re.compile(r"-?\d+y").findall(unit)[0].split("y")[0]
    else:
        penalty_yards = 0
    if team_list_in_file[0] == team_abbreviation_dict[penalty_team]:
        home_penalty_info[0] += 1
        home_penalty_info[1] += int(penalty_yards)
    else:
        visitor_penalty_info[0] += 1
        visitor_penalty_info[1] += int(penalty_yards)
    return home_penalty_info, visitor_penalty_info
