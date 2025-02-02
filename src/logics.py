import re
import pymupdf

from logger import logger


def get_yards(
    pdf_document: pymupdf.Document, team_name_list: list[str], is_run: bool
) -> dict:
    """
    Extracts yardage statistics from a PDF document for specified teams.
    Args:
        pdf_document (pymupdf.Document): The PDF document to be analyzed.
        team_name_list (list[str]): A list of team names to search for in the document.
        is_run (bool): If True, search for running yards; if False, search for passing yards.
    Returns:
        dict: A dictionary containing the extracted yardage statistics for each team.
              The dictionary has the following structure:
              [
                  {"name": "TeamName1", "texts": [list of yardages]},
                  {"name": "TeamName2", "texts": [list of yardages]}
              ]
    Raises:
        ValueError: If the number of teams found in the document is not equal to 2.
    """
    # 正規表現パターンを作成
    if is_run:
        search_format = re.compile(r"-?\d+yラン")
        parse_keyword = "yラン"
    else:
        search_format = re.compile(r"-?\d+yパス")
        parse_keyword = "yパス"
    # 全ページをループして特定の書式のテキストを抽出
    extracted_text_dict_list = [{"name": "", "texts": []}, {"name": "", "texts": []}]

    team_list_in_file = []

    team_mode = 0

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text("text")
        units = text.split("\n")
        for unit in units:
            # 「チーム名 Time」の記法からチーム名を抽出
            if (
                unit.split(" ")[0] in team_name_list
                and unit.split(" ")[0] not in team_list_in_file
            ):
                team_list_in_file.append(unit.split(" ")[0])
            # チーム名が見つかったら、その後の記録をそのチームのものとして処理
            if unit.split(" ")[0] in team_list_in_file:
                if unit.split(" ")[0] == team_list_in_file[0]:
                    team_mode = 0
                else:
                    team_mode = 1
            matches = search_format.findall(unit)
            if matches:
                extracted_text_dict_list[team_mode]["texts"].append(
                    int(matches[0].split(parse_keyword)[0])
                )
    if len(team_list_in_file) != 2:
        logger.error("見つかったチーム数が2つではありません。")
    extracted_text_dict_list[0]["name"] = team_list_in_file[0]
    extracted_text_dict_list[1]["name"] = team_list_in_file[1]
    return extracted_text_dict_list
