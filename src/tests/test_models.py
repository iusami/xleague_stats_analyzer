import pytest
import tempfile
import json
import csv
from pathlib import Path
from models import (
    Config, ThirdDownStats, PenaltyInfo, RedzoneInfo, PassingAttempsInfo,
    BreakDownStatsInfo, SeriesStatsInfo, FumbleInfo, KickoffReturnInfo,
    PuntInfo, FGInfo, StartingFieldPosition, TimePossession, PRInfo,
    TouchDownInfo, Stats
)


class TestConfig:
    """Configモデルのテスト"""
    
    def test_config_creation(self):
        config = Config(run_long_gain_threshold=15, pass_long_gain_threshold=20)
        assert config.run_long_gain_threshold == 15
        assert config.pass_long_gain_threshold == 20
    
    def test_config_validation(self):
        # 正常なケース
        config = Config(run_long_gain_threshold=10, pass_long_gain_threshold=25)
        assert config.run_long_gain_threshold == 10
        assert config.pass_long_gain_threshold == 25


class TestThirdDownStats:
    """ThirdDownStatsモデルのテスト"""
    
    def test_third_down_stats_creation(self):
        stats = ThirdDownStats(third_down_success=5, third_down_numbers=10)
        assert stats.third_down_success == 5
        assert stats.third_down_numbers == 10


class TestPenaltyInfo:
    """PenaltyInfoモデルのテスト"""
    
    def test_penalty_info_creation(self):
        penalty = PenaltyInfo(count=3, yards=25)
        assert penalty.count == 3
        assert penalty.yards == 25


class TestRedzoneInfo:
    """RedzoneInfoモデルのテスト"""
    
    def test_redzone_info_creation(self):
        redzone = RedzoneInfo(
            play_count=5, fg_score_count=2, touchdown_count=3, series_count=4
        )
        assert redzone.play_count == 5
        assert redzone.fg_score_count == 2
        assert redzone.touchdown_count == 3
        assert redzone.series_count == 4


class TestPassingAttempsInfo:
    """PassingAttempsInfoモデルのテスト"""
    
    def test_passing_attempts_info_creation(self):
        passing = PassingAttempsInfo(attempts=20, completion=15, interception=1)
        assert passing.attempts == 20
        assert passing.completion == 15
        assert passing.interception == 1


class TestBreakDownStatsInfo:
    """BreakDownStatsInfoモデルのテスト"""
    
    def test_breakdown_stats_info_creation(self):
        passing_info = PassingAttempsInfo(attempts=20, completion=15, interception=1)
        breakdown = BreakDownStatsInfo(
            team_name="Team A",
            opponent_name="Team B", 
            run_gain=150,
            run_play=25,
            pass_gain=200,
            passing_attempts_info=passing_info
        )
        assert breakdown.team_name == "Team A"
        assert breakdown.opponent_name == "Team B"
        assert breakdown.run_gain == 150
        assert breakdown.run_play == 25
        assert breakdown.pass_gain == 200
        assert breakdown.passing_attempts_info.attempts == 20


class TestStartingFieldPosition:
    """StartingFieldPositionモデルのテスト"""
    
    def test_starting_field_position_creation(self):
        field_data = [
            {"team_name": "Team A", "opponent_name": "Team B", "field_position": 25, "score": 0},
            {"team_name": "Team A", "opponent_name": "Team B", "field_position": 50, "score": 7}
        ]
        position = StartingFieldPosition(field_position=field_data)
        assert len(position.field_position) == 2
        assert position.field_position[0]["team_name"] == "Team A"
        assert position.field_position[1]["field_position"] == 50
    
    def test_save_as_json(self):
        field_data = [
            {"team_name": "Team A", "opponent_name": "Team B", "field_position": 25, "score": 0}
        ]
        position = StartingFieldPosition(field_position=field_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            position.save_as_json(temp_path)
            
            # ファイルが作成されたことを確認
            assert temp_path.exists()
            
            # ファイル内容を確認
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "field_position" in data
            assert len(data["field_position"]) == 1
            assert data["field_position"][0]["team_name"] == "Team A"
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_save_as_csv(self):
        field_data = [
            {"team_name": "Team A", "opponent_name": "Team B", "field_position": 25, "score": 0},
            {"team_name": "Team A", "opponent_name": "Team B", "field_position": 50, "score": 7}
        ]
        position = StartingFieldPosition(field_position=field_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            position.save_as_csv(temp_path)
            
            # ファイルが作成されたことを確認
            assert temp_path.exists()
            
            # ファイル内容を確認
            with open(temp_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 2
            assert rows[0]["team_name"] == "Team A"
            assert rows[0]["field_position"] == "25"
            assert rows[1]["field_position"] == "50"
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestStats:
    """Statsモデルのテスト"""
    
    def create_sample_stats(self):
        """テスト用のStatsオブジェクトを作成"""
        config = Config(run_long_gain_threshold=15, pass_long_gain_threshold=20)
        third_down_stats = ThirdDownStats(third_down_success=6, third_down_numbers=12)
        penalty_info = PenaltyInfo(count=3, yards=25)
        fumble_info = FumbleInfo(fumble=1, lost=0)
        redzone_info = RedzoneInfo(play_count=5, fg_score_count=1, touchdown_count=2, series_count=3)
        passing_info = PassingAttempsInfo(attempts=25, completion=18, interception=1)
        team_stats_info = BreakDownStatsInfo(
            team_name="Team A", opponent_name="Team B", run_gain=150, run_play=20,
            pass_gain=200, passing_attempts_info=passing_info
        )
        series_info = SeriesStatsInfo(series_count=8, score_count=3)
        kickoff_return_stats = KickoffReturnInfo(return_num=3, return_yards=75)
        punt_stats = PuntInfo(punt_num=4, punt_yards=160)
        fg_stats = FGInfo(fg_success=2, fg_blocks=0, fg_block_yards=0, fg_trials=3, fg_good_trial_yards=45)
        time_possession = TimePossession(minutes=28, seconds=30)
        pr_info = PRInfo(return_num=2, return_yards=15)
        
        return Stats(
            team_score=21,
            offense_score=18,
            run_yards=[5, 12, 18, 3, 25, 8],  # 18と25が閾値15を超える
            pass_yards=[8, 15, 22, 35, 12],   # 22と35が閾値20を超える
            third_down_stats=third_down_stats,
            penalty_info=penalty_info,
            fumble_info=fumble_info,
            redzone_info=redzone_info,
            team_stats_info=team_stats_info,
            series_info=series_info,
            config=config,
            kickoff_return_stats=kickoff_return_stats,
            punt_stats=punt_stats,
            fg_stats=fg_stats,
            time_possession=time_possession,
            pr_info=pr_info,
            run_td=2,
            pass_td=1
        )
    
    def test_stats_creation(self):
        stats = self.create_sample_stats()
        assert stats.team_score == 21
        assert stats.offense_score == 18
        assert stats.team_stats_info.team_name == "Team A"
        assert stats.run_td == 2
        assert stats.pass_td == 1
    
    def test_big_run_count_calculation(self):
        stats = self.create_sample_stats()
        # run_yards=[5, 12, 18, 3, 25, 8] で閾値15を超えるのは18と25
        assert stats.big_run_count == 2
    
    def test_big_pass_count_calculation(self):
        stats = self.create_sample_stats()
        # pass_yards=[8, 15, 22, 35, 12] で閾値20を超えるのは22と35
        assert stats.big_pass_count == 2
    
    def test_third_down_success_rate_calculation(self):
        stats = self.create_sample_stats()
        # 6/12 * 100 = 50%
        assert stats.third_down_success_rate == 50
    
    def test_count_large_run_yards(self):
        stats = self.create_sample_stats()
        # 閾値10で確認
        count = stats._count_large_run_yards(10)
        # run_yards=[5, 12, 18, 3, 25, 8] で10を超えるのは12, 18, 25
        assert count == 3
    
    def test_count_large_pass_yards(self):
        stats = self.create_sample_stats()
        # 閾値15で確認
        count = stats._count_large_pass_yards(15)
        # pass_yards=[8, 15, 22, 35, 12] で15を超えるのは22, 35
        assert count == 2
    
    def test_third_down_rate_calculation(self):
        stats = self.create_sample_stats()
        rate = stats._get_third_down_rate()
        assert rate == 50  # 6/12 * 100 = 50


class TestTimePossession:
    """TimePossessionモデルのテスト"""
    
    def test_time_possession_creation(self):
        time_pos = TimePossession(minutes=25, seconds=30)
        assert time_pos.minutes == 25
        assert time_pos.seconds == 30


class TestPRInfo:
    """PRInfoモデルのテスト"""
    
    def test_pr_info_creation(self):
        pr_info = PRInfo(return_num=3, return_yards=45)
        assert pr_info.return_num == 3
        assert pr_info.return_yards == 45


class TestTouchDownInfo:
    """TouchDownInfoモデルのテスト"""
    
    def test_touchdown_info_creation(self):
        td_info = TouchDownInfo(run_touchdown=2, pass_touchdown=3)
        assert td_info.run_touchdown == 2
        assert td_info.pass_touchdown == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
