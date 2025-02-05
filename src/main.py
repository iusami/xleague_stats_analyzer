from pathlib import Path
import click

from logger import logger
from logics import get_yards
from break_team_stats import get_third_down_info
from models import Stats
from utils import load_config_from_file, load_team_names_from_file, open_pdf


@click.command()
@click.argument("pdf_path", type=Path)
@click.argument("config_path", type=Path, default="config.json")
def main(pdf_path: Path, config_path: Path):
    config = load_config_from_file(config_path)
    team_names_list = load_team_names_from_file("teams.json")
    pdf_document = open_pdf(pdf_path)
    team_extracted_yards = get_yards(pdf_document, team_names_list)
    team_third_down_stats = get_third_down_info(pdf_document)
    for extracted_yards, third_down_stats in [
        (
            team_extracted_yards.home_team_extracted_yards,
            team_third_down_stats.home_team_third_down_stats,
        ),
        (
            team_extracted_yards.visitor_team_extracted_yards,
            team_third_down_stats.visitor_team_third_down_stats,
        ),
    ]:
        stats = Stats(
            team_name=extracted_yards.team_name,
            run_yards=extracted_yards.rushing_yards,
            pass_yards=extracted_yards.passing_yards,
            third_down_stats=third_down_stats,
        )
        logger.info(
            "%s had %d runs greater than 15 yards.",
            stats.team_name,
            stats.count_large_run_yards(config.run_long_gain_threshold),
        )
        logger.info(
            "%s had %d passes greater than 20 yards.",
            stats.team_name,
            stats.count_large_pass_yards(config.pass_long_gain_threshold),
        )
        logger.info(
            "%s had a third down conversion rate of %.2d%%.",
            stats.team_name,
            stats.get_third_down_rate(),
        )


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
