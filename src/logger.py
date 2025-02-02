import logging

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# コンソールハンドラーの設定
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# フォーマッターの設定
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
ch.setFormatter(formatter)

# ハンドラーをロガーに追加
logger.addHandler(ch)
