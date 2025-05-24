import pymupdf
from logger import logger
from models import TeamStartingFieldPosition, StartingFieldPosition


def get_drive_chart_page(pdf_document: pymupdf.Document):
    margin = 3
    same_line_words = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        words = page.get_text()
        tmp_same_line = []
        current_y0 = 0
        if "ドライブチャート" in words:
            current_words = page.get_text("words")
            for word in current_words:
                if word[1] - current_y0 < margin:
                    tmp_same_line.append(word[4])
                else:
                    same_line_words.append(" ".join(tmp_same_line))
                    tmp_same_line = [word[4]]
                    current_y0 = word[1]
            drive_chart_idx = same_line_words.index("ドライブチャート")
            return same_line_words[drive_chart_idx:]
    raise ValueError("ドライブチャートが見つかりません")


def get_starting_field_position(
    pdf_document: pymupdf.Document,
    team_name_in_file: list[str],
    team_abbreviation_in_file: list[str],
) -> TeamStartingFieldPosition:
    same_line_words = get_drive_chart_page(pdf_document)
    start_ct = 0
    team_index = 0
    home_field_position_dict_list = []
    visitor_field_position_dict_list = []
    for ct, word in enumerate(same_line_words):
        for team_name in team_name_in_file:
            if team_name in word:
                team_index = team_name_in_file.index(team_name)
        logger.debug("word in get fp: %s", word)
        if "攻守交代時プレイ" in word:
            logger.debug("攻守交代時プレイが見つかりました。")
            start_ct = ct + 1
            for word in same_line_words[start_ct:]:
                logger.debug("word in get_stating_field_position: %s", word)
                # if word in team_name_in_file:
                #     break
                if any(team_name in word for team_name in team_name_in_file):
                    logger.debug("Team name is found in starting fp process")
                    break
                split_words = word.split(" ")
                for ct, split_word in enumerate(split_words):
                    if split_word in team_abbreviation_in_file:
                        split_word_index = team_abbreviation_in_file.index(split_word)
                        if split_word_index == team_index:
                            field_position = split_words[ct + 1]
                        else:
                            field_position = 100 - int(split_words[ct + 1])
                        if "Good" in split_words or "TouchDown" in split_words:
                            field_pos_dict = {
                                "team_name": team_name_in_file[team_index],
                                "opponent_name": team_name_in_file[1 - team_index],
                                "field_position": int(field_position),
                                "score": 1,
                            }
                        else:
                            field_pos_dict = {
                                "team_name": team_name_in_file[team_index],
                                "opponent_name": team_name_in_file[1 - team_index],
                                "field_position": int(field_position),
                                "score": 0,
                            }
                        if team_index == 0:
                            home_field_position_dict_list.append(field_pos_dict)
                        else:
                            visitor_field_position_dict_list.append(field_pos_dict)
                        logger.debug("field_pos: %s", field_pos_dict)
                        break
    return TeamStartingFieldPosition(
        home_team_starting_field_position=StartingFieldPosition(
            field_position=home_field_position_dict_list
        ),
        visitor_team_starting_field_position=StartingFieldPosition(
            field_position=visitor_field_position_dict_list,
        ),
    )
