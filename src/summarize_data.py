import polars as pl
from glob import glob
import os
import click
from logger import logger

# カラム名の変更を指定する辞書
column_mapping = {
    "team_score": "得点",
    "offense_score": "攻撃得点",
    "third_down_stats_third_down_success": "3rdダウン成功数",
    "third_down_stats_third_down_numbers": "3rdダウン試行数",
    "penalty_info_count": "反則回数",
    "penalty_info_yards": "反則ヤード",
    "fumble_info_fumble": "ファンブル回数",
    "fumble_info_lost": "ファンブルロスト回数",
    "redzone_info_count": "レッドゾーン攻撃回数",
    "redzone_info_touchdown": "レッドゾーンTD数",
    "team_stats_info_team_name": "チーム名",
    "team_stats_info_opponent_name": "相手チーム名",
    "team_stats_info_run_gain": "ラン獲得ヤード",
    "team_stats_info_run_play": "ラン試行数",
    "team_stats_info_pass_gain": "パス獲得ヤード",
    "team_stats_info_passing_attempts_info_attempts": "パス試行数",
    "team_stats_info_passing_attempts_info_completion": "パス成功数",
    "team_stats_info_passing_attempts_info_interception": "被インターセプト数",
    "series_info_series_count": "シリーズ数",
    "series_info_score_count": "シリーズ得点回数",
    "kickoff_return_stats_return_num": "キックオフリターン回数",
    "kickoff_return_stats_return_yards": "キックオフリターン獲得ヤード",
    "punt_stats_punt_num": "パント回数",
    "punt_stats_punt_yards": "パント獲得ヤード",
    "fg_stats_fg_success": "FG成功数",
    "fg_stats_fg_blocks": "FGブロック数",
    "fg_stats_fg_block_yards": "FGブロックヤード",
    "fg_stats_fg_trials": "FG試行数",
    "fg_stats_fg_good_trial_yards": "FG成功ヤード",
    "time_possession_minutes": "ポゼッション時間(分)",
    "time_possession_seconds": "ポゼッション時間(秒)",
    "pr_info_return_num": "パントリターン回数",
    "pr_info_return_yards": "パントリターンヤード",
    "big_run_count": "15yds以上のラン回数",
    "big_pass_count": "20yds以上のパス回数",
    "third_down_success_rate": "3rdダウン成功率",
}

# カラムの順番を指定するリスト
column_order = [
    "チーム名",
    "得点",
    "攻撃得点",
    "1試合あたりの平均攻撃得点",
    "試合平均play数",
    "総獲得ヤード",
    "ラン獲得ヤード",
    "ラン試行数",
    "試合平均Run回数",
    "試合平均Run獲得ヤード",
    "1playあたりの平均ラン獲得ヤード",
    "15yds以上のラン回数",
    "パス獲得ヤード",
    "パス試行数",
    "パス成功数",
    "パス成功率",
    "試合平均Pass回数",
    "試合平均Pass獲得ヤード",
    "1playあたりの平均パス獲得ヤード",
    "20yds以上のパス回数",
    "平均ポゼッション時間(分)",
    "平均ポゼッション時間(秒)",
    "被インターセプト数",
    "3rdダウン成功数",
    "3rdダウン試行数",
    "3rdダウン成功率",
    "反則回数",
    "反則ヤード",
    "ファンブル回数",
    "ファンブルロスト回数",
    "レッドゾーン攻撃回数",
    "レッドゾーンTD数",
    "レッドゾーンスコア率",
    "シリーズ数",
    "シリーズ得点回数",
    "得点シリーズ率",
    "キックオフリターン回数",
    "キックオフリターン獲得ヤード",
    "平均キックオフリターン獲得ヤード",
    "パント回数",
    "パント獲得ヤード",
    "平均パント獲得ヤード",
    "パントリターン回数",
    "パントリターンヤード",
    "平均パントリターンヤード",
    "FG成功数",
    "FGブロック数",
    "FGブロックヤード",
    "FG試行数",
    "FG成功ヤード",
]

# 対象チームのリスト
target_teams = [
    "ノジマ相模原ライズ",
    "IBM",
    "東京ガスクリエイターズ",
    "パナソニックインパルス",
    "SEKISUIチャレンジャーズ",
    "オービックシーガルズ",
    "エレコム神戸ファイニーズ",
    "富士通フロンティアーズ",
]


def process_team_data(df: pl.DataFrame):
    # カラム名の変更
    df = df.rename(column_mapping)

    # チーム名ごとに合計してまとめる。ただし、相手チーム名の列は除く
    df_stats = df.group_by("チーム名").agg(pl.all().exclude("相手チーム名").sum())

    # 各チーム名の出現回数を計測し、"試合回数"という列に保存
    df_counts = df.group_by("チーム名").agg(pl.count("チーム名").alias("試合回数"))

    # 合計したデータと試合回数を結合
    df_stats = df_stats.join(df_counts, on="チーム名")

    # 3rdダウン成功率を計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("3rdダウン成功数") / pl.col("3rdダウン試行数") * 100)
            .round(0)
            .cast(int)
            .alias("3rdダウン成功率")
        ]
    )

    # 試合平均Run回数と試合平均Run獲得ヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("ラン試行数") / pl.col("試合回数"))
            .round(1)
            .cast(int)
            .alias("試合平均Run回数"),
            (pl.col("ラン獲得ヤード") / pl.col("ラン試行数"))
            .round(1)
            .alias("1playあたりの平均ラン獲得ヤード"),
        ]
    )

    # 1試合平均Run獲得ヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("ラン獲得ヤード") / pl.col("試合回数"))
            .round(1)
            .cast(int)
            .alias("試合平均Run獲得ヤード"),
        ]
    )
    # 1試合平均Pass獲得ヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("パス獲得ヤード") / pl.col("試合回数"))
            .round(1)
            .cast(int)
            .alias("試合平均Pass獲得ヤード"),
        ]
    )

    # 試合平均Pass回数と試合平均Pass獲得ヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("パス試行数") / pl.col("試合回数"))
            .round(1)
            .cast(int)
            .alias("試合平均Pass回数"),
            (pl.col("パス獲得ヤード") / pl.col("パス試行数"))
            .round(1)
            .alias("1playあたりの平均パス獲得ヤード"),
        ]
    )

    # ラン獲得ヤードとパス獲得ヤードを合計して"総獲得ヤード"という列を追加
    df_stats = df_stats.with_columns(
        [
            (pl.col("ラン獲得ヤード") + pl.col("パス獲得ヤード"))
            .round(1)
            .cast(int)
            .alias("総獲得ヤード")
        ]
    )

    # "ラン試行数"と"パス試行数"および"試合回数"より、"試合平均play数"を計算して列を追加
    df_stats = df_stats.with_columns(
        [
            ((pl.col("ラン試行数") + pl.col("パス試行数")) / pl.col("試合回数"))
            .round(1)
            .cast(int)
            .alias("試合平均play数")
        ]
    )

    # "レッドゾーンTD数"と"レッドゾーン攻撃回数"より"レッドゾーンスコア率"を計算して列を追加
    df_stats = df_stats.with_columns(
        [
            ((pl.col("レッドゾーンTD数") / pl.col("レッドゾーン攻撃回数")) * 100)
            .round(0)
            .cast(int)
            .alias("レッドゾーンスコア率")
        ]
    )

    # "シリーズ得点回数"と"シリーズ数"より"得点シリーズ率"を計算して列を追加
    df_stats = df_stats.with_columns(
        [
            ((pl.col("シリーズ得点回数") / pl.col("シリーズ数")) * 100)
            .round(0)
            .cast(int)
            .alias("得点シリーズ率")
        ]
    )

    # "パス成功率"を計算して列を追加
    df_stats = df_stats.with_columns(
        [(pl.col("パス成功数") / pl.col("パス試行数") * 100).round(0).cast(int).alias("パス成功率")]
    )

    # ポゼッション時間(分)から、試合平均ポゼッション時間(分)を計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("ポゼッション時間(分)") / pl.col("試合回数"))
            .round(1)
            .cast(int)
            .alias("平均ポゼッション時間(分)")
        ]
    )

    # ポゼッション時間(秒)から、試合平均ポゼッション時間(秒)を計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("ポゼッション時間(秒)") / pl.col("試合回数"))
            .round(1)
            .cast(int)
            .alias("平均ポゼッション時間(秒)")
        ]
    )

    # "ラン獲得ヤード"と"ラン試行数"より1playあたりの平均ラン獲得ヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("ラン獲得ヤード") / pl.col("ラン試行数"))
            .round(2)
            .alias("平均ラン獲得ヤード")
        ]
    )

    # "パス獲得ヤード"と"パス試行数"より、1playあたりの平均パス獲得ヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("パス獲得ヤード") / pl.col("パス試行数"))
            .round(2)
            .alias("平均パス獲得ヤード")
        ]
    )

    # 1試合あたりの平均攻撃得点を計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("攻撃得点") / pl.col("試合回数"))
            .round(1)
            .cast(int)
            .alias("1試合あたりの平均攻撃得点")
        ]
    )

    # 平均キックオフリターン獲得ヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("キックオフリターン獲得ヤード") / pl.col("キックオフリターン回数"))
            .round(1)
            .cast(int)
            .alias("平均キックオフリターン獲得ヤード")
        ]
    )

    # 平均パントリターンヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("パントリターンヤード") / pl.col("パントリターン回数"))
            .round(1)
            .cast(int)
            .alias("平均パントリターンヤード")
        ]
    )

    # 平均パント獲得ヤードを計算
    df_stats = df_stats.with_columns(
        [
            (pl.col("パント獲得ヤード") / pl.col("パント回数"))
            .round(1)
            .cast(int)
            .alias("平均パント獲得ヤード")
        ]
    )

    # "チーム名"列の値を基準に行を並び替え
    df_stats = df_stats.sort("チーム名")

    logger.info("df_statsの列名: %s", df_stats.columns)
    # カラムの順番を変更
    df_stats = df_stats.select(column_order)

    return df_stats


@click.command()
@click.argument("folder_path")
@click.argument("output_folder")
def main(folder_path, output_folder):
    # "stats"という文字列を含むcsvファイルのみを選択
    csv_list = glob(os.path.join(folder_path, "*stats*.csv"))

    # CSVファイルを読み込み、リストに格納
    df_list = [pl.read_csv(csv) for csv in csv_list]

    # データフレームを結合
    df_concat = pl.concat(df_list)

    # チーム名が含まれるデータ
    df_team = df_concat.filter(pl.col("team_stats_info_team_name").is_in(target_teams))

    # 相手チーム名が含まれるデータ
    df_opponent = df_concat.filter(
        pl.col("team_stats_info_opponent_name").is_in(target_teams)
    )

    # df_opponentの"team_stats_info_team_name"列と"team_stats_info_opponent_name"列の列名を入れ替え
    df_opponent = df_opponent.with_columns(
        [
            pl.col("team_stats_info_team_name").alias("team_stats_info_opponent_name"),
            pl.col("team_stats_info_opponent_name").alias("team_stats_info_team_name"),
        ]
    )

    # データ処理
    df_team_stats = process_team_data(df_team)
    df_opponent_stats = process_team_data(df_opponent)

    # output_folderが存在しない場合、作成
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # データを保存
    df_team_stats.write_csv(os.path.join(output_folder, "team_stats.csv"))
    df_opponent_stats.write_csv(os.path.join(output_folder, "opponent_stats.csv"))

    # 結果を表示
    print("チーム名が含まれるデータ:")
    print(df_team_stats)
    print("\n相手チーム名が含まれるデータ:")
    print(df_opponent_stats)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
