import pymupdf
from models import KickoffReturnInfo, TeamKickoffReturnInfo, TeamPuntInfo, PuntInfo


def get_personal_stats_page(pdf_document: pymupdf.Document):
    margin = 3
    same_line_words = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        words = page.get_text()
        tmp_same_line = []
        current_y0 = 0
        if "個人スタッツ" in words:
            current_words = page.get_text("words")
            for word in current_words:
                if word[1] - current_y0 < margin:
                    tmp_same_line.append(word[4])
                else:
                    same_line_words.append(" ".join(tmp_same_line))
                    tmp_same_line = [word[4]]
                    current_y0 = word[1]
            return same_line_words
    raise ValueError("個人スタッツが見つかりません")


def get_kick_off_return_stat(pdf_document: pymupdf.Document) -> TeamKickoffReturnInfo:
    same_line_words = get_personal_stats_page(pdf_document)
    ko_idx = 0
    for ct, word in enumerate(same_line_words):
        if "KICKOFF RETURNS " in word:
            ko_idx = ct
    for word in same_line_words[ko_idx:]:
        if "Total" in word:
            split_words = word.split(" ")
            home_return_num = split_words[1]
            home_return_yards = split_words[2]
            visitor_return_num = split_words[8]
            visitor_return_yards = split_words[9]
            return TeamKickoffReturnInfo(
                home_kickoff_return_info=KickoffReturnInfo(
                    return_num=int(home_return_num), return_yards=int(home_return_yards)
                ),
                visitor_kickoff_return_info=KickoffReturnInfo(
                    return_num=int(visitor_return_num),
                    return_yards=int(visitor_return_yards),
                ),
            )
    raise ValueError("KICKOFF RETURNS data not found")


def get_punt_stat(pdf_document: pymupdf.Document) -> TeamPuntInfo:
    same_line_words = get_personal_stats_page(pdf_document)
    ko_idx = 0
    for ct, word in enumerate(same_line_words):
        if "PUNTING" in word:
            ko_idx = ct
    for word in same_line_words[ko_idx:]:
        if "Total" in word:
            split_words = word.split(" ")
            home_return_num = split_words[1]
            home_return_yards = split_words[2]
            visitor_return_num = split_words[9]
            visitor_return_yards = split_words[10]
            return TeamPuntInfo(
                home_punt_info=PuntInfo(
                    punt_num=int(home_return_num), punt_yards=int(home_return_yards)
                ),
                visitor_punt_info=PuntInfo(
                    punt_num=int(visitor_return_num),
                    punt_yards=int(visitor_return_yards),
                ),
            )
    raise ValueError("KICKOFF RETURNS data not found")
