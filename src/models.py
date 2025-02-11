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
    count: int
    touchdown: int


class TeamRedzoneInfo(BaseModel):
    home_team_redzone_info: RedzoneInfo
    visitor_team_redzone_info: RedzoneInfo


class Stats(BaseModel):
    team_name: str
    run_yards: list[int]
    pass_yards: list[int]
    third_down_stats: ThirdDownStats
    penalty_info: PenaltyInfo
    redzone_info: RedzoneInfo
    config: Config
    big_run_count: int = 0
    big_pass_count: int = 0
    third_down_success_rate: int = 0

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
