import csv
import json
from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    run_long_gain_threshold: int
    pass_long_gain_threshold: int


class ThirdDownStats(BaseModel):
    third_down_success: int
    third_down_numbers: int


class TeamThirdDownStats(BaseModel):
    home_team_third_down_stats: ThirdDownStats
    visitor_team_third_down_stats: ThirdDownStats


class PenaltyInfo(BaseModel):
    count: int
    yards: int


class TeamPenaltyInfo(BaseModel):
    home_team_penalty_info: PenaltyInfo
    visitor_team_penalty_info: PenaltyInfo


class RedzoneInfo(BaseModel):
    play_count: int
    fg_score_count: int
    touchdown_count: int
    series_count: int


class TeamRedzoneInfo(BaseModel):
    home_team_redzone_info: RedzoneInfo
    visitor_team_redzone_info: RedzoneInfo


class PassingAttempsInfo(BaseModel):
    attempts: int
    completion: int
    interception: int


class TeamPassingAttemptsInfo(BaseModel):
    home_info: PassingAttempsInfo
    visitor_info: PassingAttempsInfo


class BreakDownStatsInfo(BaseModel):
    team_name: str
    opponent_name: str
    run_gain: int
    run_play: int
    pass_gain: int
    passing_attempts_info: PassingAttempsInfo


class TeamBreakDownStatsInfo(BaseModel):
    home_team_break_down_stats: BreakDownStatsInfo
    visitor_team_break_down_stats: BreakDownStatsInfo


class SeriesStatsInfo(BaseModel):
    series_count: int
    score_count: int


class TeamSeriesStatsInfo(BaseModel):
    home_series_stats: SeriesStatsInfo
    visitor_series_stats: SeriesStatsInfo


class FumbleInfo(BaseModel):
    fumble: int
    lost: int


class TeamFumbleInfo(BaseModel):
    home_team_fumble_info: FumbleInfo
    visitor_team_fumble_info: FumbleInfo


class KickoffReturnInfo(BaseModel):
    return_num: int
    return_yards: int


class TeamKickoffReturnInfo(BaseModel):
    home_kickoff_return_info: KickoffReturnInfo
    visitor_kickoff_return_info: KickoffReturnInfo


class PuntInfo(BaseModel):
    punt_num: int
    punt_yards: int


class TeamPuntInfo(BaseModel):
    home_punt_info: PuntInfo
    visitor_punt_info: PuntInfo


class FGInfo(BaseModel):
    fg_success: int
    fg_blocks: int
    fg_block_yards: int
    fg_trials: int
    fg_good_trial_yards: int


class TeamFGInfo(BaseModel):
    home_fg_info: FGInfo
    visitor_fg_info: FGInfo


class StartingFieldPosition(BaseModel):
    field_position: list[dict[str, object]]

    def save_as_json(self, file_path: Path) -> None:
        """
        Saves the starting field position of the team as a JSON file.

        Args:
            file_path (str): The file path to save the JSON file.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                self.model_dump(),
                f,
                ensure_ascii=False,
                indent=4,
            )

    def save_as_csv(self, file_path: Path) -> None:
        """
        Saves the starting field position of the team as a CSV file.

        Args:
            file_path (str): The file path to save the CSV file.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["team_name", "opponent_name", "field_position", "score"]
            )
            writer.writeheader()
            for field_pos in self.field_position:
                writer.writerow(field_pos)


class TeamStartingFieldPosition(BaseModel):
    home_team_starting_field_position: StartingFieldPosition
    visitor_team_starting_field_position: StartingFieldPosition

    def save_each_position_as_json(self, file_path: str) -> None:
        """
        Saves the starting field position of each team as a JSON file.

        Args:
            file_path (str): The file path to save the JSON file.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                self.model_dump(),
                f,
                ensure_ascii=False,
                indent=4,
            )


class TimePossession(BaseModel):
    minutes: int
    seconds: int


class TeamTimePossession(BaseModel):
    home_team_time_possession: TimePossession
    visitor_team_time_possession: TimePossession


class PRInfo(BaseModel):
    return_num: int
    return_yards: int


class TeamPRInfo(BaseModel):
    home_team_PRInfo: PRInfo
    visitor_team_PRInfo: PRInfo


class TouchDownInfo(BaseModel):
    run_touchdown: int
    pass_touchdown: int


class TeamTouchDownInfo(BaseModel):
    home_team_touchdown_info: TouchDownInfo
    visitor_team_touchdown_info: TouchDownInfo


class Stats(BaseModel):
    team_score: int
    offense_score: int
    run_yards: list[int]
    pass_yards: list[int]
    third_down_stats: ThirdDownStats
    penalty_info: PenaltyInfo
    fumble_info: FumbleInfo
    redzone_info: RedzoneInfo
    team_stats_info: BreakDownStatsInfo
    series_info: SeriesStatsInfo
    config: Config
    kickoff_return_stats: KickoffReturnInfo
    punt_stats: PuntInfo
    fg_stats: FGInfo
    time_possession: TimePossession
    pr_info: PRInfo
    big_run_count: int = 0
    big_pass_count: int = 0
    third_down_success_rate: int = 0
    run_td: int = 0
    pass_td: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        self.big_run_count = self._count_large_run_yards(
            self.config.run_long_gain_threshold
        )
        self.big_pass_count = self._count_large_pass_yards(
            self.config.pass_long_gain_threshold
        )
        self.third_down_success_rate = self._get_third_down_rate()

    def _count_large_run_yards(self, threshold: int) -> int:
        """
        Counts the number of run yards greater than the given threshold.

        Args:
            threshold (int): The threshold value to compare run yards against.

        Returns:
            int: The count of run yards greater than the threshold.
        """
        return sum(1 for yard in self.run_yards if yard > threshold)

    def _count_large_pass_yards(self, threshold: int) -> int:
        """
        Counts the number of pass yards greater than the given threshold.

        Args:
            threshold (int): The threshold value to compare pass yards against.

        Returns:
            int: The count of pass yards greater than the threshold.
        """
        return sum(1 for yard in self.pass_yards if yard > threshold)

    def _get_third_down_rate(self) -> int:
        """
        Calculates the third down conversion rate.

        Returns:
            float: The third down conversion rate.
        """
        return int(
            (
                self.third_down_stats.third_down_success
                / self.third_down_stats.third_down_numbers
            )
            * 100
        )
