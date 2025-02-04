import pymupdf
from models import ThirdDownStats

def GetThirdDownInfo(pdf_document: pymupdf.Document) -> ThirdDownStats:
    # 1枚目のページを取得
    page = pdf_document.load_page(0)

    # 行単位でテキストを出力
    text = page.get_text("text")
    lines = text.split('\n')

    third_down_idx = None
    for ct, line in enumerate(lines):
        if "3rd Down" in line:
            third_down_idx = ct

    if third_down_idx is None:
        raise ValueError("3rd Downの情報が見つかりませんでした。")

    # "3rd Down コンバージョン"と書かれた箇所の次にホームチームの3rdダウン成功数と試行数が記載されている
    # その次にビジターチームの3rdダウン成功数と試行数が記載されている
    home_team_3rd_down_success = lines[third_down_idx+1].split("(")[0].split("/")[0]
    home_team_3rd_down_numbers = lines[third_down_idx+1].split("(")[0].split("/")[1]
    visitor_team_3rd_down_success = lines[third_down_idx+2].split("(")[0].split("/")[0]
    visitor_team_3rd_down_numbers = lines[third_down_idx+2].split("(")[0].split("/")[1]

    return ThirdDownStats(
        third_down_success=home_team_3rd_down_success,
        third_down_numbers=home_team_3rd_down_numbers
    ), ThirdDownStats(
        third_down_success=visitor_team_3rd_down_success,
        third_down_numbers=visitor_team_3rd_down_numbers
    )
