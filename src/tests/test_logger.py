import pytest
import logging
from unittest.mock import patch, MagicMock
from logger import logger, set_log_level


class TestLogger:
    """loggerモジュールのテスト"""
    
    def test_logger_exists(self):
        """loggerが存在することを確認"""
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    def test_logger_name(self):
        """loggerの名前が正しいことを確認"""
        assert logger.name == "logger"
    
    def test_logger_has_handler(self):
        """loggerにハンドラーが設定されていることを確認"""
        assert len(logger.handlers) > 0
        # StreamHandlerが設定されていることを確認
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) > 0


class TestSetLogLevel:
    """set_log_level関数のテスト"""
    
    def setup_method(self):
        """各テストの前にログレベルをリセット"""
        logger.setLevel(logging.DEBUG)
    
    def test_set_log_level_debug(self):
        """DEBUGレベルの設定テスト"""
        set_log_level("DEBUG")
        assert logger.level == logging.DEBUG
    
    def test_set_log_level_info(self):
        """INFOレベルの設定テスト"""
        set_log_level("INFO")
        assert logger.level == logging.INFO
    
    def test_set_log_level_warning(self):
        """WARNINGレベルの設定テスト"""
        set_log_level("WARNING")
        assert logger.level == logging.WARNING
    
    def test_set_log_level_error(self):
        """ERRORレベルの設定テスト"""
        set_log_level("ERROR")
        assert logger.level == logging.ERROR
    
    @patch.object(logger, 'warning')
    def test_set_log_level_invalid(self, mock_warning):
        """無効なログレベルの設定テスト"""
        set_log_level("INVALID")
        
        # INFOレベルに設定されることを確認
        assert logger.level == logging.INFO
        
        # 警告メッセージが出力されることを確認
        mock_warning.assert_called_once_with("ログレベルが不正です。INFOに設定します。")
    
    def test_set_log_level_case_sensitive(self):
        """大文字小文字の区別テスト"""
        # 小文字では無効として扱われる
        with patch.object(logger, 'warning') as mock_warning:
            set_log_level("debug")
            assert logger.level == logging.INFO
            mock_warning.assert_called_once()
    
    def test_set_log_level_empty_string(self):
        """空文字列の場合のテスト"""
        with patch.object(logger, 'warning') as mock_warning:
            set_log_level("")
            assert logger.level == logging.INFO
            mock_warning.assert_called_once()
    
    def test_set_log_level_none(self):
        """Noneの場合のテスト"""
        with patch.object(logger, 'warning') as mock_warning:
            set_log_level(None)
            assert logger.level == logging.INFO
            mock_warning.assert_called_once()


class TestLoggerIntegration:
    """loggerの統合テスト"""
    
    def test_logger_output_levels(self, caplog):
        """各ログレベルでの出力テスト"""
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
        
        # ログメッセージが記録されていることを確認
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
    
    def test_logger_level_filtering(self, caplog):
        """ログレベルによるフィルタリングテスト"""
        # WARNINGレベルに設定
        set_log_level("WARNING")
        
        with caplog.at_level(logging.WARNING):
            logger.debug("Debug message")  # 出力されない
            logger.info("Info message")    # 出力されない
            logger.warning("Warning message")  # 出力される
            logger.error("Error message")      # 出力される
        
        # WARNING以上のメッセージのみ記録されていることを確認
        assert "Debug message" not in caplog.text
        assert "Info message" not in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
