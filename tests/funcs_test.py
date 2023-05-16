import os
import pytest
import tempfile
import requests

from unittest.mock import patch, mock_open, MagicMock

from funcs import generate_report_name, update_curriculum, generate_pdf_file_and_upload, check_report_state


def test_generate_report_name():
    assert generate_report_name(2022, 1) == '1_2022-2023'
    assert generate_report_name(2022, 2) == '2_2021-2022'
    assert generate_report_name(2023, 1) == '1_2023-2024'
    assert generate_report_name(2023, 2) == '2_2022-2023'


@pytest.fixture
def mock_pdf_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as f:
        f.write(b'sample text')
        yield f.name
    os.unlink(f.name)


def test_generate_pdf_file_and_upload_success(mock_pdf_file, monkeypatch):
    monkeypatch.setattr(requests, 'post',
        lambda *args, **kwargs: type('Response', (), {'status_code': 200, 'json': lambda: {'result': 'success'}})())

    assert generate_pdf_file_and_upload(2022, 2) == {'success': True,
        'message':                                              'Итоговый отчёт успешно сформирован и добавлен на сервер ИМИТ.'}

    os.unlink(mock_pdf_file.replace('.docx', '.pdf'))


def test_generate_pdf_file_and_upload_wrong_file_path(monkeypatch):
    monkeypatch.setattr('os.path.exists', lambda path: False)

    assert generate_pdf_file_and_upload(2022, 2) == {'success': False, 'errortype': 'wrong current file path',
        'message':                                              'Отчёт не найден.'}


def test_generate_pdf_file_and_upload_invalid_pdf(mock_pdf_file, monkeypatch):
    def mock_convert(*args, **kwargs):
        raise RuntimeError('pdf conversion failed')

    monkeypatch.setattr('docx2pdf.convert', mock_convert)

    assert generate_pdf_file_and_upload(2022, 2) == {'success': False, 'errortype': 'report convert',
        'message':                                              'Произошла ошибка при конвертации .pdf отчёта.'}

    assert not os.path.exists(mock_pdf_file.replace('.docx', '.pdf'))


def test_generate_pdf_file_and_upload_adding_pdf_error(mock_pdf_file, monkeypatch):
    monkeypatch.setattr(requests, 'post',
        lambda *args, **kwargs: type('Response', (), {'status_code': 500, 'json': lambda: {'result': 'failure'}})())

    assert generate_pdf_file_and_upload(2022, 2) == {'success': False, 'errortype': 'adding pdf to IMIT',
        'message':                                              'Ошибка при добавлении итогового отчёта на сервер ИМИТ.'}

    os.unlink(mock_pdf_file.replace('.docx', '.pdf'))


class TestUpdateCurriculum:
    @pytest.fixture(autouse=True)
    def setup_class(self):
        self.success_response = {"success": True, "message": "Учебная информация была успешно обновлена."}
        self.config_path = "config.txt"
        self.config_line = "example_config_line"

    def test_no_config_file(self):
        with patch("myapp.funcs.CONFIG_PLAN_FILES_PATH", "incorrect_path"):
            assert update_curriculum().json == {"success": False, "errortype": "config file access",
                "message":                                 "Не найден конфигурационный файл."}

    def test_config_file_not_found(self):
        with patch("myapp.funcs.open", side_effect=FileNotFoundError):
            assert update_curriculum().json == {"success": False, "errortype": "config file access",
                "message":                                 "Не найден конфигурационный файл."}

    def test_insertInDataBase_returns_error(self, mocker):
        mock_insert = mocker.patch("myapp.curriculum_importer.insertInDataBase")
        mock_insert.return_value = {"success": False, "message": "Ошибка при обновлении учебной информации."}
        with patch("builtins.open", MagicMock(return_value=["some_config_line"])):
            assert update_curriculum().json == mock_insert.return_value

    def test_insertInDataBase_returns_none(self, mocker):
        mock_insert = mocker.patch("myapp.curriculum_importer.insertInDataBase")
        mock_insert.return_value = None
        with patch("builtins.open", MagicMock(return_value=["some_config_line"])):
            assert update_curriculum().json == self.success_response

    def test_multiple_config_lines(self, mocker):
        mock_insert = mocker.patch("myapp.curriculum_importer.insertInDataBase")
        mock_insert.return_value = None
        with patch("builtins.open", MagicMock(return_value=["line1", "line2", "line3"])):
            assert update_curriculum().json == self.success_response
        mock_insert.assert_called_with("line1")
        mock_insert.assert_called_with("line2")
        mock_insert.assert_called_with("line3")

    def test_insertInDataBase_exception(self, mocker):
        mock_insert = mocker.patch("myapp.curriculum_importer.insertInDataBase")
        mock_insert.side_effect = Exception("Some error")
        with patch("builtins.open", MagicMock(return_value=[self.config_line])):
            assert update_curriculum().json == {"success": False, "errortype": "server error",
                "message":                                 "Ошибка при обновлении учебной информации."}

    def test_insertInDataBase_calls(self, mocker):
        mock_insert = mocker.patch("myapp.curriculum_importer.insertInDataBase")
        mock_insert.return_value = None
        with patch("builtins.open", MagicMock(return_value=[self.config_line])):
            assert update_curriculum().json == self.success_response
        mock_insert.assert_called_with(self.config_line)

    def test_insertInDataBase_multiple_calls(self, mocker):
        mock_insert = mocker.patch("myapp.curriculum_importer.insertInDataBase")
        mock_insert.return_value = None
        with patch("builtins.open", MagicMock(return_value=[self.config_line, self.config_line])):
            assert update_curriculum().json == self.success_response
        mock_insert.assert_called_with(self.config_line)
        assert mock_insert.call_count == 2
