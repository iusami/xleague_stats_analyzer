import re
import pymupdf  # type: ignore  # noqa
from pydantic import BaseModel

from models import (
    PenaltyInfo,
    TeamPenaltyInfo,
    RedzoneInfo,
    TeamRedzoneInfo,
    SeriesStatsInfo,
    TeamSeriesStatsInfo,
)
from logger import logger
from utils import open_pdf_to_list_only_page


class ExtractedYards(BaseModel):
    team_name: str
    rushing_yards: list[int]
    passing_yards: list[int]


class TeamsExtractedYards(BaseModel):
    home_team_extracted_yards: ExtractedYards
    visitor_team_extracted_yards: ExtractedYards


def get_yards(
    pdf_document: pymupdf.Document,
    team_abbreviation_dict: dict[str, str],
    team_list_in_file: list[str],
) -> tuple[TeamsExtractedYards, TeamPenaltyInfo]:
    """
    Extracts and returns the rushing and passing yards,
    as well as penalty information for two teams from a given PDF document.
    Args:
        pdf_document (pymupdf.Document): The PDF document containing the game statistics.
        team_name_list (tuple[str]):
            A tuple containing the names of the teams to look for in the document.
        team_abbreviation_dict (dict[str, str]):
            A dictionary mapping team names to their abbreviations.
    Returns:
        tuple[TeamsExtractedYards, TeamPenaltyInfo]: A tuple containing two elements:
            - TeamsExtractedYards:
                An object containing the extracted rushing and passing yards for both the home and visitor teams.
            - TeamPenaltyInfo:
                An object containing the penalty information for both the home and visitor teams.
    Raises:
        ValueError: If the number of teams found in the document is not equal to 2.
    """
    # 全ページをループして特定の書式のテキストを抽出
    home_extracted_yards: tuple[list[int], list[int]] = ([], [])
    home_penalty_info: list[int] = [0, 0]
    visitor_extracted_yards: tuple[list[int], list[int]] = ([], [])
    visitor_penalty_info: list[int] = [0, 0]

    team_mode = 0

    # 全ページのテキストを一度に取得
    units = get_text_units(pdf_document)

    # unitsの中から"Play by Play"の後の記録を抽出
    for ct, unit in enumerate(units):
        if "Play by Play" in unit:
            units = units[ct + 1 :]
            break

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

        home_penalty_info, visitor_penalty_info = extract_penalty_info(
            home_penalty_info,
            visitor_penalty_info,
            team_list_in_file,
            unit,
            team_abbreviation_dict,
        )

        if "Lineups" in unit:
            break

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


def get_text_units(pdf_document):
    all_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        all_text += page.get_text("text") + "\n"

    units = all_text.split("\n")
    return units


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
    if "+Penalty" not in unit:
        return home_penalty_info, visitor_penalty_info
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


def get_redzone_info(
    same_line_words_list: list[str],
    team_list_in_file: list[str],
    team_abbreviation_in_file: list[str],
) -> TeamRedzoneInfo:
    team_mode = 0
    home_redzone_info = [0, 0]
    visitor_redzone_info = [0, 0]
    play_by_play_idx = same_line_words_list.index("Play by Play First Quarter")
    for unit in same_line_words_list[play_by_play_idx + 1 :]:
        for word in unit.split(" "):
            if word in team_list_in_file:
                team_mode = team_list_in_file.index(word)
        if "RUN" not in unit and "PASS" not in unit and "FG" not in unit:
            continue
        offense_team = team_abbreviation_in_file[team_mode]
        defense_team = team_abbreviation_in_file[1 - team_mode]
        unit_split = unit.split(" ")

        team_idx = next(
            (
                i
                for i, word in enumerate(unit_split)
                if word in [offense_team, defense_team]
            ),
            None,
        )
        if team_idx is None:
            continue
        field_position = int(unit_split[team_idx + 1])
        if (field_position > 25) or (unit_split[team_idx] == offense_team):
            continue
        if "Lineups" in unit:
            break
        if team_mode == 0:
            home_redzone_info[0] += 1
            # Touchdownはプレーカウントとスコアをカウント
            if "TOUCHDOWN" in unit:
                home_redzone_info[1] += 1
            # FGはスコアのみカウント
            if "FG" in unit and "GOOD" in unit:
                home_redzone_info[0] -= 1
                home_redzone_info[1] += 1
        else:
            visitor_redzone_info[0] += 1
            if "TOUCHDOWN" in unit:
                visitor_redzone_info[1] += 1
            if "FG" in unit and "GOOD" in unit:
                visitor_redzone_info[0] -= 1
                visitor_redzone_info[1] += 1

    return TeamRedzoneInfo(
        home_team_redzone_info=RedzoneInfo(
            count=home_redzone_info[0], touchdown=home_redzone_info[1]
        ),
        visitor_team_redzone_info=RedzoneInfo(
            count=visitor_redzone_info[0], touchdown=visitor_redzone_info[1]
        ),
    )


def get_series(
    pdf_document: pymupdf.Document, team_list_in_file: list[str]
) -> TeamSeriesStatsInfo:
    start_home_drive_idx = None
    end_home_drive_idx = None
    start_visitor_drive_idx = None
    end_visitor_drive_idx = None
    drive_chart = open_pdf_to_list_only_page(pdf_document, 2)
    for ct, line in enumerate(drive_chart):
        if team_list_in_file[0] in line:
            start_home_drive_idx = ct + 3
        if team_list_in_file[1] in line:
            end_home_drive_idx = ct - 1
            start_visitor_drive_idx = ct + 3
        if "攻撃時間" in line:
            end_visitor_drive_idx = ct - 1
            break
    if start_home_drive_idx is None:
        raise ValueError("ホームチームのドライブチャートが見つかりません")
    if end_home_drive_idx is None:
        raise ValueError("ホームチームのドライブチャートの終わりが見つかりません")
    if start_visitor_drive_idx is None:
        raise ValueError("ビジターチームのドライブチャートが見つかりません")
    if end_visitor_drive_idx is None:
        raise ValueError("ビジターチームのドライブチャートの終わりが見つかりません")
    logger.debug(
        "start/end home drive idx %s/%s", start_home_drive_idx, end_home_drive_idx
    )
    logger.debug("start home line: %s", drive_chart[start_home_drive_idx])
    logger.debug("end home line: %s", drive_chart[end_home_drive_idx])
    logger.debug("start visitor drive idx %s", start_visitor_drive_idx)
    logger.debug("start visitor line: %s", drive_chart[start_visitor_drive_idx])
    logger.debug("end visitor drive idx %s", end_visitor_drive_idx)
    logger.debug("end visitor line: %s", drive_chart[end_visitor_drive_idx])

    def count_series_and_scores(start_idx, end_idx):
        series_count = end_idx - start_idx + 1
        score_count = sum(
            1
            for line in drive_chart[start_idx:end_idx]
            if "TouchDown" in line or "FG Good" in line
        )
        return series_count, score_count

    home_series_count, home_score_count = count_series_and_scores(
        start_home_drive_idx, end_home_drive_idx
    )
    visitor_series_count, visitor_score_count = count_series_and_scores(
        start_visitor_drive_idx, end_visitor_drive_idx
    )

    return TeamSeriesStatsInfo(
        home_series_stats=SeriesStatsInfo(
            series_count=home_series_count, score_count=home_score_count
        ),
        visitor_series_stats=SeriesStatsInfo(
            series_count=visitor_series_count, score_count=visitor_score_count
        ),
    )
