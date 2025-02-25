from pathlib import Path
import click

from logger import logger, set_log_level
from logics import get_yards, get_redzone_info, get_series
from break_drive_chart import get_starting_field_position
from break_team_stats import (
    break_down_team_stats,
    get_third_down_info,
    extract_fumble,
    extract_score,
    extract_fg_stats,
    extract_time_possession
)
from break_personal_stats import get_kick_off_return_stat, get_punt_stat
from models import Stats
from utils import (
    load_config_from_file,
    load_team_names_from_file,
    open_pdf,
    open_pdf_to_list,
    open_pdf_to_list_only_page,
    export_stats_to_json,
    export_stats_to_csv,
)


@click.command()
@click.argument("pdf_path", type=Path)
@click.argument("config_path", type=Path, default="config.json")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
)
def main(pdf_path: Path, config_path: Path, log_level: str):
    set_log_level(log_level)
    config = load_config_from_file(config_path)
    team_names_list, team_abbreviation_dict, team_abbreviation_by_team_dict = (
        load_team_names_from_file("teams.json")
    )
    pdf_document = open_pdf(pdf_path)

    same_line_words_list = open_pdf_to_list(pdf_path)
    team_break_down_stats_info = break_down_team_stats(pdf_document, team_names_list)
    team_list_in_file = [
        team_break_down_stats_info.home_team_break_down_stats.team_name,
        team_break_down_stats_info.visitor_team_break_down_stats.team_name,
    ]
    logger.info("Team names: %s", team_list_in_file)
    team_abbreviation_in_file = [
        team_abbreviation_by_team_dict[team] for team in team_list_in_file
    ]
    team_extracted_yards, team_penalty_info = get_yards(
        pdf_document,
        team_abbreviation_dict,
        team_list_in_file,
    )

    team_third_down_stats = get_third_down_info(pdf_document)
    team_redzone_info = get_redzone_info(
        same_line_words_list, team_list_in_file, team_abbreviation_in_file
    )
    team_series_info = get_series(pdf_document, team_list_in_file)
    team_fumble_info = extract_fumble(same_line_words_list)
    score_tuple = extract_score(open_pdf_to_list_only_page(pdf_document, 0))

    team_kickoff_return_stats = get_kick_off_return_stat(pdf_document)
    team_punt_stats = get_punt_stat(pdf_document)
    team_fg_stats = extract_fg_stats(same_line_words_list, team_list_in_file)
    team_time_possession = extract_time_possession(open_pdf_to_list_only_page(pdf_document, 0))
    team_starting_field_position = get_starting_field_position(
        pdf_document, team_list_in_file, team_abbreviation_in_file
    )
    # team_starting_field_position.save_each_position_as_json("field_position.json")
    team_starting_field_position.home_team_starting_field_position.save_as_json(
        Path("home_field_position.json")
    )
    team_starting_field_position.home_team_starting_field_position.save_as_csv(
        Path("home_field_position.csv")
    )
    team_starting_field_position.visitor_team_starting_field_position.save_as_json(
        Path("visitor_field_position.json")
    )
    team_starting_field_position.visitor_team_starting_field_position.save_as_csv(
        Path("visitor_field_position.csv")
    )
    logger.debug("team_starting_field_position: %s", team_starting_field_position)
    for ct, (
        extracted_yards,
        third_down_stats,
        penalty_info,
        redzone_info,
        team_stats_info,
        series_info,
        fumble_info,
        score,
        kickoff_return_stats,
        punt_stats,
        fg_stats,
        time_possession
    ) in enumerate(
        [
            (
                team_extracted_yards.home_team_extracted_yards,
                team_third_down_stats.home_team_third_down_stats,
                team_penalty_info.home_team_penalty_info,
                team_redzone_info.home_team_redzone_info,
                team_break_down_stats_info.home_team_break_down_stats,
                team_series_info.home_series_stats,
                team_fumble_info.home_team_fumble_info,
                score_tuple[0],
                team_kickoff_return_stats.home_kickoff_return_info,
                team_punt_stats.home_punt_info,
                team_fg_stats.home_fg_info,
                team_time_possession.home_team_time_possession
            ),
            (
                team_extracted_yards.visitor_team_extracted_yards,
                team_third_down_stats.visitor_team_third_down_stats,
                team_penalty_info.visitor_team_penalty_info,
                team_redzone_info.visitor_team_redzone_info,
                team_break_down_stats_info.visitor_team_break_down_stats,
                team_series_info.visitor_series_stats,
                team_fumble_info.visitor_team_fumble_info,
                score_tuple[1],
                team_kickoff_return_stats.visitor_kickoff_return_info,
                team_punt_stats.visitor_punt_info,
                team_fg_stats.visitor_fg_info,
                team_time_possession.visitor_team_time_possession   
            ),
        ]
    ):
        stats = Stats(
            team_score=score,
            run_yards=extracted_yards.rushing_yards,
            pass_yards=extracted_yards.passing_yards,
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
            time_possession=time_possession
        )
        logger.info(
            "%s had %d runs greater than 15 yards.",
            stats.team_stats_info.team_name,
            stats.big_run_count,
        )
        logger.info(
            "%s had %d passes greater than 20 yards.",
            stats.team_stats_info.team_name,
            stats.big_pass_count,
        )
        logger.info(
            "%s had a third down conversion rate of %.2d%%.",
            stats.team_stats_info.team_name,
            stats.third_down_success_rate,
        )
        logger.info(
            "%s did %d times penalty of %d yards.",
            stats.team_stats_info.team_name,
            stats.penalty_info.count,
            stats.penalty_info.yards,
        )
        logger.info(
            "%s had %d redzone attempts and %d scores.",
            stats.team_stats_info.team_name,
            stats.redzone_info.count,
            stats.redzone_info.touchdown,
        )
        export_stats_to_json(stats, Path(f"stats_{ct}.json"))
        export_stats_to_csv(stats, Path(f"stats_{ct}.csv"))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
