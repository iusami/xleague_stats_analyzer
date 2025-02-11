import logging

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# コンソールハンドラーの設定
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# フォーマッターの設定
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
ch.setFormatter(formatter)

# ハンドラーをロガーに追加
logger.addHandler(ch)


def set_log_level(level: str):
    match level:
        case "DEBUG":
            logger.setLevel(logging.DEBUG)
        case "INFO":
            logger.setLevel(logging.INFO)
        case "WARNING":
            logger.setLevel(logging.WARNING)
        case "ERROR":
            logger.setLevel(logging.ERROR)
        case _:
            logger.setLevel(logging.INFO)
            logger.warning("ログレベルが不正です。INFOに設定します。")
