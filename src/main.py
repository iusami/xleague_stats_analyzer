from pathlib import Path
import click

from logger import logger
from logics import get_yards, get_team_info, get_text_units, get_redzone_info
from break_team_stats import get_third_down_info
from models import Stats
from utils import (
    load_config_from_file,
    load_team_names_from_file,
    open_pdf,
    open_pdf_to_list,
)


@click.command()
@click.argument("pdf_path", type=Path)
@click.argument("config_path", type=Path, default="config.json")
def main(pdf_path: Path, config_path: Path):
    config = load_config_from_file(config_path)
    team_names_list, team_abbreviation_dict, team_abbreviation_by_team_dict = (
        load_team_names_from_file("teams.json")
    )
    pdf_document = open_pdf(pdf_path)
    units = get_text_units(pdf_document)
    team_list_in_file, team_abbreviation_in_file = get_team_info(
        team_names_list, team_abbreviation_by_team_dict, units
    )
    same_line_words_list = open_pdf_to_list(pdf_path)
    team_extracted_yards, team_penalty_info = get_yards(
        pdf_document,
        team_names_list,
        team_abbreviation_dict,
        team_abbreviation_by_team_dict,
    )

    team_third_down_stats = get_third_down_info(pdf_document)
    team_redzone_info = get_redzone_info(
        same_line_words_list, team_list_in_file, team_abbreviation_in_file
    )
    for extracted_yards, third_down_stats, penalty_info, redzone_info in [
        (
            team_extracted_yards.home_team_extracted_yards,
            team_third_down_stats.home_team_third_down_stats,
            team_penalty_info.home_team_penalty_info,
            team_redzone_info.home_team_redzone_info,
        ),
        (
            team_extracted_yards.visitor_team_extracted_yards,
            team_third_down_stats.visitor_team_third_down_stats,
            team_penalty_info.visitor_team_penalty_info,
            team_redzone_info.visitor_team_redzone_info,
        ),
    ]:
        stats = Stats(
            team_name=extracted_yards.team_name,
            run_yards=extracted_yards.rushing_yards,
            pass_yards=extracted_yards.passing_yards,
            third_down_stats=third_down_stats,
            penalty_info=penalty_info,
            redzone_info=redzone_info,
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
        logger.info(
            "%s did %d times penalty of %d yards.",
            stats.team_name,
            stats.penalty_info.count,
            stats.penalty_info.yards,
        )
        logger.info(
            "%s had %d redzone attempts and %d scores.",
            stats.team_name,
            stats.redzone_info.count,
            stats.redzone_info.touchdown,
        )


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
