from pathlib import Path
import click

from logger import logger
from logics import get_yards
from break_team_stats import get_3rd_down_info
from models import Stats
from utils import load_config_from_file, load_team_names_from_file, open_pdf


@click.command()
@click.argument("pdf_path", type=Path)
@click.option("--config", type=Path, default="config.json")
def main(pdf_path: Path, config: Path):
    config = load_config_from_file("config.json")
    team_names_list = load_team_names_from_file("teams.json")
    pdf_document = open_pdf(pdf_path)
    run_yards_dict_list = get_yards(pdf_document, team_names_list, True)
    pass_yards_dict_list = get_yards(pdf_document, team_names_list, False)
    third_down_stats = get_3rd_down_info(pdf_document)
    for index in range(2):
        stats = Stats(
            run_yards=run_yards_dict_list[index]["texts"],
            pass_yards=pass_yards_dict_list[index]["texts"],
            third_down_stats=third_down_stats[index],
        )
        logger.info(
            "%s had %d runs greater than 15 yards.",
            run_yards_dict_list[index]["name"],
            stats.count_large_run_yards(config.run_long_gain_threshold),
        )
        logger.info(
            "%s had %d passes greater than 20 yards.",
            pass_yards_dict_list[index]["name"],
            stats.count_large_pass_yards(config.pass_long_gain_threshold),
        )
        logger.info(
            "%s had a third down conversion rate of %.2d%%.",
            run_yards_dict_list[index]["name"],
            stats.get_third_down_rate()
        )


if __name__ == "__main__":
    main()
