from pydantic import BaseModel


class Config(BaseModel):
    run_long_gain_threshold: int
    pass_long_gain_threshold: int

class ThirdDownStats(BaseModel):
    third_down_success: int
    third_down_numbers: int

class Stats(BaseModel):
    run_yards: list[int]
    pass_yards: list[int]
    third_down_stats: ThirdDownStats

    def count_large_run_yards(self, threshold: int) -> int:
        """
        Counts the number of run yards greater than the given threshold.

        Args:
            threshold (int): The threshold value to compare run yards against.

        Returns:
            int: The count of run yards greater than the threshold.
        """
        return sum(1 for yard in self.run_yards if yard > threshold)

    def count_large_pass_yards(self, threshold: int) -> int:
        """
        Counts the number of pass yards greater than the given threshold.

        Args:
            threshold (int): The threshold value to compare pass yards against.

        Returns:
            int: The count of pass yards greater than the threshold.
        """
        return sum(1 for yard in self.pass_yards if yard > threshold)

    def get_third_down_rate(self) -> float:
        """
        Calculates the third down conversion rate.

        Returns:
            float: The third down conversion rate.
        """
        return (self.third_down_stats.third_down_success / self.third_down_stats.third_down_numbers) * 100
