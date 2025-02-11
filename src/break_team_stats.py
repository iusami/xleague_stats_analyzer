import pymupdf  # type: ignore  # noqa
from models import (
    TeamBreakDownStatsInfo,
    ThirdDownStats,
    TeamThirdDownStats,
    BreakDownStatsInfo,
    PassingAttempsInfo,
    TeamPassingAttemptsInfo,
)
from logger import logger
from utils import open_pdf_to_list_only_page


def get_third_down_info(pdf_document: pymupdf.Document) -> TeamThirdDownStats:
    # 1枚目のページを取得
    page = pdf_document.load_page(0)

    # 行単位でテキストを出力
    text = page.get_text("text")
    lines = text.split("\n")

    third_down_idx = None
    for ct, line in enumerate(lines):
        if "3rd Down" in line:
            third_down_idx = ct

    if third_down_idx is None:
        raise ValueError("3rd Downの情報が見つかりませんでした。")

    # "3rd Down コンバージョン"と書かれた箇所の次にホームチームの3rdダウン成功数と試行数が記載されている
    # その次にビジターチームの3rdダウン成功数と試行数が記載されている
    home_team_3rd_down_success = lines[third_down_idx + 1].split("(")[0].split("/")[0]
    home_team_3rd_down_numbers = lines[third_down_idx + 1].split("(")[0].split("/")[1]
    visitor_team_3rd_down_success = (
        lines[third_down_idx + 2].split("(")[0].split("/")[0]
    )
    visitor_team_3rd_down_numbers = (
        lines[third_down_idx + 2].split("(")[0].split("/")[1]
    )

    return TeamThirdDownStats(
        home_team_third_down_stats=ThirdDownStats(
            third_down_success=home_team_3rd_down_success,
            third_down_numbers=home_team_3rd_down_numbers,
        ),
        visitor_team_third_down_stats=ThirdDownStats(
            third_down_success=visitor_team_3rd_down_success,
            third_down_numbers=visitor_team_3rd_down_numbers,
        ),
    )


def extract_stat(same_line_words, stat_name):
    for line in same_line_words:
        words = [word for word in line.split(" ") if word]
        if stat_name in line:
            logger.debug("%sが見つかりました。", stat_name)
            logger.debug(words)
            return words[1], words[2]
    raise ValueError(f"{stat_name}が見つかりませんでした。")


def extract_pass_attempts(same_line_words, stat_name) -> TeamPassingAttemptsInfo:
    for line in same_line_words:
        words = [word for word in line.split(" ") if word]
        if stat_name in line:
            logger.debug("%sが見つかりました。", stat_name)
            logger.debug(words)
            home_attempts, home_completion, home_interception = words[-2].split("-")
            visitor_attempts, visitor_completion, visitor_interception = words[
                -1
            ].split("-")
            return TeamPassingAttemptsInfo(
                home_info=PassingAttempsInfo(
                    attempts=int(home_attempts),
                    completion=int(home_completion),
                    interception=int(home_interception),
                ),
                visitor_info=PassingAttempsInfo(
                    attempts=int(visitor_attempts),
                    completion=int(visitor_completion),
                    interception=int(visitor_interception),
                ),
            )

    raise ValueError(f"{stat_name}が見つかりませんでした。")


def break_down_team_stats(
    pdf_document: pymupdf.Document, team_name_list: list[str]
) -> TeamBreakDownStatsInfo:
    same_line_words = open_pdf_to_list_only_page(pdf_document, 0)

    home_team_name, visitor_team_name = get_home_visitor_team_name(
        team_name_list, same_line_words
    )

    team_passing_attempts_info = extract_pass_attempts(same_line_words, "試投数")

    home_run_gain, visitor_run_gain = extract_stat(same_line_words, "RUN獲得ヤード数")
    home_run_play, visitor_run_play = extract_stat(same_line_words, "RUNプレイ数")
    home_pass_gain, visitor_pass_gain = extract_stat(same_line_words, "PASS獲得ヤード")

    return TeamBreakDownStatsInfo(
        home_team_break_down_stats=BreakDownStatsInfo(
            team_name=home_team_name,
            run_gain=home_run_gain,
            run_play=home_run_play,
            pass_gain=home_pass_gain,
            passing_attempts_info=team_passing_attempts_info.home_info,
        ),
        visitor_team_break_down_stats=BreakDownStatsInfo(
            team_name=visitor_team_name,
            run_gain=visitor_run_gain,
            run_play=visitor_run_play,
            pass_gain=visitor_pass_gain,
            passing_attempts_info=team_passing_attempts_info.visitor_info,
        ),
    )


def get_home_visitor_team_name(team_name_list, same_line_words):
    home_team_name = None
    visitor_team_name = None
    for line in same_line_words:
        if "ホーム" in line:
            words = [word for word in line.split(" ") if word]
            for team_name in team_name_list:
                if team_name in words:
                    home_team_name = team_name
        if "ビジター" in line:
            words = [word for word in line.split(" ") if word]
            for team_name in team_name_list:
                if team_name in words:
                    visitor_team_name = team_name
    if home_team_name is None or visitor_team_name is None:
        raise ValueError("ホームチーム名またはビジターチーム名が見つかりませんでした。")
    return home_team_name, visitor_team_name
