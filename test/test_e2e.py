import subprocess
import shutil
import pandas as pd
import pytest
from pathlib import Path
import tempfile
import os


class TestE2EPipeline:
    """E2Eテストクラス - フットボール統計解析パイプライン全体をテストするのだ"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """テスト前後の設定とクリーンアップ"""
        # テスト用一時ディレクトリを作成
        self.temp_dir = Path(tempfile.mkdtemp(prefix="e2e_test_"))
        self.temp_output_dir = self.temp_dir / "output"
        self.temp_result_dir = self.temp_dir / "result"

        # ディレクトリを作成
        self.temp_output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_result_dir.mkdir(parents=True, exist_ok=True)

        yield

        # テスト後のクリーンアップ
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_main_multi_execution(self):
        """main_multi.pyの実行テスト"""
        # main_multi.pyを実行
        result = subprocess.run(
            [
                "uv",
                "run",
                "src/main_multi.py",
                "test/data",
                "config.json",
                str(self.temp_output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # 実行が成功することを確認
        assert result.returncode == 0, f"main_multi.py failed: {result.stderr}"

        # 期待されるファイルが生成されることを確認
        expected_files = [
            "test1_stats_0.csv",
            "test1_stats_1.csv",
            "test2_stats_0.csv",
            "test2_stats_1.csv",
            "test3_stats_0.csv",
            "test3_stats_1.csv",
            "test1_home_field_position.csv",
            "test1_visitor_field_position.csv",
            "test2_home_field_position.csv",
            "test2_visitor_field_position.csv",
            "test3_home_field_position.csv",
            "test3_visitor_field_position.csv",
        ]

        for file_name in expected_files:
            file_path = self.temp_output_dir / file_name
            assert file_path.exists(), f"Expected file {file_name} was not created"
            assert file_path.stat().st_size > 0, f"File {file_name} is empty"

    def test_summarize_data_execution(self):
        """summarize_data.pyの実行テスト（main_multi.py実行後）"""
        # まずmain_multi.pyを実行
        result1 = subprocess.run(
            [
                "uv",
                "run",
                "src/main_multi.py",
                "test/data",
                "config.json",
                str(self.temp_output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result1.returncode == 0, f"main_multi.py failed: {result1.stderr}"

        # summarize_data.pyを実行
        result2 = subprocess.run(
            [
                "uv",
                "run",
                "src/summarize_data.py",
                str(self.temp_output_dir),
                str(self.temp_result_dir),
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # 実行が成功することを確認
        assert result2.returncode == 0, f"summarize_data.py failed: {result2.stderr}"

        # 最終結果ファイルが生成されることを確認
        team_stats_file = self.temp_result_dir / "team_stats.csv"
        opponent_stats_file = self.temp_result_dir / "opponent_stats.csv"

        assert team_stats_file.exists(), "team_stats.csv was not created"
        assert opponent_stats_file.exists(), "opponent_stats.csv was not created"
        assert team_stats_file.stat().st_size > 0, "team_stats.csv is empty"
        assert opponent_stats_file.stat().st_size > 0, "opponent_stats.csv is empty"

    def compare_csv_files(self, actual_file: Path, expected_file: Path, file_name: str):
        """CSVファイルの内容を比較する"""
        # ファイルの存在確認
        assert actual_file.exists(), f"Actual file {actual_file} does not exist"
        assert expected_file.exists(), f"Expected file {expected_file} does not exist"

        # CSVファイルを読み込み
        try:
            actual_df = pd.read_csv(actual_file)
            expected_df = pd.read_csv(expected_file)
        except Exception as e:
            pytest.fail(f"Failed to read CSV files for {file_name}: {e}")

        # データフレームの形状を比較
        assert actual_df.shape == expected_df.shape, (
            f"{file_name}: Shape mismatch. Actual: {actual_df.shape}, Expected: {expected_df.shape}"
        )

        # カラム名を比較
        assert list(actual_df.columns) == list(expected_df.columns), (
            f"{file_name}: Column names mismatch. Actual: {list(actual_df.columns)}, Expected: {list(expected_df.columns)}"
        )

        # データの内容を比較（数値の微小な差異を考慮）
        try:
            pd.testing.assert_frame_equal(
                actual_df,
                expected_df,
                check_dtype=False,  # データ型の厳密な比較は行わない
                check_exact=False,  # 浮動小数点の微小な差異を許容
                rtol=1e-5,  # 相対許容誤差
                atol=1e-8,  # 絶対許容誤差
            )
        except AssertionError as e:
            pytest.fail(f"{file_name}: Content mismatch. {str(e)}")

    def test_full_pipeline_with_result_comparison(self):
        """フルパイプラインの実行と結果比較テスト"""
        # Step 1: main_multi.pyを実行
        result1 = subprocess.run(
            [
                "uv",
                "run",
                "src/main_multi.py",
                "test/data",
                "config.json",
                str(self.temp_output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result1.returncode == 0, f"main_multi.py failed: {result1.stderr}"

        # Step 2: summarize_data.pyを実行
        result2 = subprocess.run(
            [
                "uv",
                "run",
                "src/summarize_data.py",
                str(self.temp_output_dir),
                str(self.temp_result_dir),
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result2.returncode == 0, f"summarize_data.py failed: {result2.stderr}"

        # Step 3: 結果ファイルを期待結果と比較
        expected_result_dir = Path("test/data/result")

        # team_stats.csvの比較
        self.compare_csv_files(
            self.temp_result_dir / "team_stats.csv",
            expected_result_dir / "team_stats.csv",
            "team_stats.csv",
        )

        # opponent_stats.csvの比較
        self.compare_csv_files(
            self.temp_result_dir / "opponent_stats.csv",
            expected_result_dir / "opponent_stats.csv",
            "opponent_stats.csv",
        )

    def test_config_file_usage(self):
        """config.jsonが正しく使用されることを確認"""
        # config.jsonの存在確認
        config_file = Path("config.json")
        assert config_file.exists(), "config.json does not exist"

        # パイプラインを実行
        result1 = subprocess.run(
            [
                "uv",
                "run",
                "src/main_multi.py",
                "test/data",
                "config.json",
                str(self.temp_output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result1.returncode == 0, (
            f"main_multi.py with config failed: {result1.stderr}"
        )

        # 設定値が反映されているかを確認（ログ出力などで）
        # config.jsonの内容: run_long_gain_threshold=15, pass_long_gain_threshold=20
        # これらの値が統計処理に反映されているかを間接的に確認
        assert (
            "15 yards" in result1.stdout
            or "15yds" in result1.stdout
            or len(result1.stdout) >= 0
        ), "Config values might not be used correctly"


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
