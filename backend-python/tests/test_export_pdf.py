"""
PDF导出模块测试
测试PDF生成核心逻辑、字体处理、XML转义
"""
import pytest
from app.api.v1.export_pdf import (
    _escape_xml,
    _make_cell_paragraph,
    get_chinese_font_name,
    parse_photos,
    get_image_url_or_path,
    _get_table_styles,
)


class TestEscapeXml:
    def test_empty_string(self):
        assert _escape_xml("") == ""

    def test_none_value(self):
        assert _escape_xml(None) == ""

    def test_ampersand_escaped(self):
        assert _escape_xml("A&B") == "A&amp;B"

    def test_angle_brackets_escaped(self):
        assert _escape_xml("<tag>") == "&lt;tag&gt;"

    def test_newline_to_br(self):
        assert _escape_xml("line1\nline2") == "line1<br/>line2"

    def test_mixed_special_chars(self):
        result = _escape_xml("A<B&C>\nD")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "<br/>" in result

    def test_numeric_input(self):
        assert _escape_xml(123) == "123"


class TestParsePhotos:
    def test_none_input(self):
        assert parse_photos(None) == []

    def test_empty_string(self):
        assert parse_photos("") == []

    def test_valid_json_list(self):
        result = parse_photos('["url1", "url2"]')
        assert len(result) == 2
        assert result[0] == "url1"

    def test_invalid_json(self):
        assert parse_photos("not json") == []

    def test_non_list_json(self):
        assert parse_photos('{"key": "value"}') == []


class TestGetChineseFontName:
    def test_returns_string(self):
        font_name = get_chinese_font_name()
        assert isinstance(font_name, str)
        assert len(font_name) > 0


class TestGetTableStyles:
    def test_returns_two_styles(self):
        info_style, log_style = _get_table_styles()
        assert info_style is not None
        assert log_style is not None

    def test_styles_have_font(self):
        info_style, log_style = _get_table_styles()
        font_name = get_chinese_font_name()
        for style in [info_style, log_style]:
            for cmd in style.getCommands():
                if cmd[0] == 'FONTNAME':
                    assert cmd[3] == font_name


class TestGetImageUrlOrPath:
    def test_empty_path(self):
        assert get_image_url_or_path("") == ""

    def test_data_image_url(self):
        assert get_image_url_or_path("data:image/png;base64,abc") == "data:image/png;base64,abc"

    def test_http_url_passthrough(self):
        assert get_image_url_or_path("http://example.com/img.jpg") == "http://example.com/img.jpg"

    def test_https_url_passthrough(self):
        assert get_image_url_or_path("https://example.com/img.jpg") == "https://example.com/img.jpg"

    def test_non_upload_path(self):
        assert get_image_url_or_path("some/other/path") == "some/other/path"
