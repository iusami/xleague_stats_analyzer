import pymupdf  # type: ignore  # noqa
from logics import get_fg_blocks, get_good_fg_trial_yards
from models import (
    TeamBreakDownStatsInfo,
    ThirdDownStats,
    TeamThirdDownStats,
    BreakDownStatsInfo,
    PassingAttempsInfo,
    TeamPassingAttemptsInfo,
    FumbleInfo,
    TeamFumbleInfo,
    FGInfo,
    TeamFGInfo,
    TimePossession,
    TeamTimePossession,
)
from logger import logger
from utils import open_pdf_to_list_only_page
import re


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


def extract_fumble(same_line_words: list[str]) -> TeamFumbleInfo:
    for line in same_line_words:
        words = [word for word in line.split(" ") if word]
        if "FUMBLE" in line:
            logger.debug("%sが見つかりました。", "FUMBLE")
            logger.debug(words)
            home_fumble, home_lost = words[-2].split("-")
            visitor_fumble, visitor_lost = words[-1].split("-")
            return TeamFumbleInfo(
                home_team_fumble_info=FumbleInfo(
                    fumble=int(home_fumble),
                    lost=int(home_lost),
                ),
                visitor_team_fumble_info=FumbleInfo(
                    fumble=int(visitor_fumble),
                    lost=int(visitor_lost),
                ),
            )
    raise ValueError("FUMBLEが見つかりませんでした。")


def extract_fg_stats(
    same_line_words: list[str], team_list_in_file: list[str]
) -> TeamFGInfo:
    home_fg = None
    home_fg_success = None
    visitor_fg = None
    visitor_fg_success = None
    for line in same_line_words:
        words = [word for word in line.split(" ") if word]
        if "Field Goal成功数" in line:
            logger.debug("%sが見つかりました。", "FG")
            logger.debug(words)
            home_fg_success, home_fg = words[-2].split("-")
            visitor_fg_success, visitor_fg = words[-1].split("-")
    if (
        home_fg is None
        or visitor_fg is None
        or home_fg_success is None
        or visitor_fg_success is None
    ):
        raise ValueError("FGが見つかりませんでした。")
    home_fg_blocks, home_fg_block_yards, visitor_fg_blocks, visitor_fg_block_yards = (
        get_fg_blocks(same_line_words, team_list_in_file)
    )
    home_fg_trials, visitor_fg_trials = get_good_fg_trial_yards(
        same_line_words, team_list_in_file
    )
    return TeamFGInfo(
        home_fg_info=FGInfo(
            fg_success=int(home_fg_success),
            fg_blocks=int(home_fg_blocks),
            fg_block_yards=int(home_fg_block_yards),
            fg_trials=int(home_fg),
            fg_good_trial_yards=int(home_fg_trials),
        ),
        visitor_fg_info=FGInfo(
            fg_success=int(visitor_fg_success),
            fg_blocks=int(visitor_fg_blocks),
            fg_block_yards=int(visitor_fg_block_yards),
            fg_trials=int(visitor_fg),
            fg_good_trial_yards=int(visitor_fg_trials),
        ),
    )


def extract_score(same_line_words: list[str]) -> tuple[int, int]:
    home_score = None
    visitor_score = None
    for line in same_line_words:
        words = [word for word in line.split(" ") if word]
        if "ホーム" in line:
            logger.debug("%sが見つかりました。", "得点")
            logger.debug(words)
            home_score = int(words[-1])
        if "ビジター" in line:
            logger.debug("%sが見つかりました。", "得点")
            logger.debug(words)
            visitor_score = int(words[-1])
        if home_score is not None and visitor_score is not None:
            return home_score, visitor_score
    raise ValueError("得点が見つかりませんでした。")


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
            opponent_name=visitor_team_name,
            run_gain=home_run_gain,
            run_play=home_run_play,
            pass_gain=home_pass_gain,
            passing_attempts_info=team_passing_attempts_info.home_info,
        ),
        visitor_team_break_down_stats=BreakDownStatsInfo(
            team_name=visitor_team_name,
            opponent_name=home_team_name,
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
        if "vs" in line:
            pattern = re.compile("|".join(re.escape(team) for team in team_name_list))
            matches = pattern.findall(line)
            if len(matches) == 2:
                home_team_name, visitor_team_name = matches
                break
    if home_team_name is None or visitor_team_name is None:
        raise ValueError("ホームチーム名またはビジターチーム名が見つかりませんでした。")
    return home_team_name, visitor_team_name


def extract_time_possession(same_line_words) -> TeamTimePossession:
    for line in same_line_words:
        words = [word for word in line.split(" ") if word]
        if "攻撃時間" in line:
            logger.debug("%sが見つかりました。", "攻撃時間")
            logger.debug(words)
            home_possession_time_min, home_possession_time_sec = words[-2].split(":")
            visitor_possession_time_min, visitor_possession_time_sec = words[-1].split(
                ":"
            )
            return TeamTimePossession(
                home_team_time_possession=TimePossession(
                    minutes=int(home_possession_time_min),
                    seconds=int(home_possession_time_sec),
                ),
                visitor_team_time_possession=TimePossession(
                    minutes=int(visitor_possession_time_min),
                    seconds=int(visitor_possession_time_sec),
                ),
            )
    raise ValueError("攻撃時間が見つかりませんでした。")


def extract_pr_yards(same_line_words: list[str]) -> tuple[int, int]:
    home_pr_yards = None
    visitor_pr_yards = None
    for line in same_line_words:
        words = [word for word in line.split(" ") if word]
        if "PUNTリターン" in line:
            logger.debug("%sが見つかりました。", "PR")
            logger.debug(words)
            if "--" in words[-2]:
                home_pr_yards = int("-" + words[-2].split("--")[1])
            else:
                home_pr_yards = int(words[-2].split("-")[1])
            if "--" in words[-1]:
                visitor_pr_yards = int("-" + words[-1].split("--")[1])
            else:
                visitor_pr_yards = int(words[-1].split("-")[1])
        if home_pr_yards is not None and visitor_pr_yards is not None:
            return home_pr_yards, visitor_pr_yards
    raise ValueError("PRヤード数が見つかりませんでした。")
