import json
import unittest
import flask

from unittest.mock import patch

import funcs
from funcs import generate_report_name, check_report_state, generate_report, \
    generate_pdf_file_and_upload

from autoreport import app


class TestGenerateReportName(unittest.TestCase):
    def test_B6_1_positive_generate_report_name(self):
        assert generate_report_name(2023, 1) == '1_2023-2024'

    def test_B6_2_positive_generate_report_name(self):
        assert generate_report_name(2023, 2) == '2_2023-2024'


class TestCheckReportState(unittest.TestCase):
    def test_B6_3_positive_check_report_state(self):
        with patch('report_status.get_status') as mock_get_status,\
                patch('funcs.generate_report') as mock_generate_report:
            mock_get_status.return_value = None
            mock_generate_report.return_value = 'generate_report()'
            result = check_report_state(2023, 1, warned=False, use_current=False, mode='generate', file=None,
                pract_data=None)
            assert result == 'generate_report()'

    def test_B6_4_positive_check_report_state(self):
        with patch('report_status.get_status') as mock_get_status,\
                patch('funcs.generate_report') as mock_generate_report,\
                app.app_context():
            assert funcs.current_file_path == ''
            mock_get_status.return_value = [2023, 1, 0, 'my_path']
            result = check_report_state(2023, 1, warned=False, use_current=True, mode='generate', file=None,
                pract_data=None)
            assert funcs.current_file_path == 'my_path'
            assert 'Второе состояние страницы' in result
            assert 'Year = 2023, Semester = 1' in result

    def test_B6_5_positive_check_report_state(self):
        with patch('report_status.get_status') as mock_get_status,\
                patch('funcs.generate_report') as mock_generate_report:
            mock_get_status.return_value = None
            mock_generate_report.return_value = 'generate_report()'
            result = check_report_state(2023, 1, warned=True, use_current=False, mode='generate', file=None,
                pract_data=None)
            assert result == 'generate_report()'

    def test_B6_6_positive_check_report_state(self):
        with patch('report_status.get_status') as mock_get_status,\
                patch('funcs.load_new_report') as mock_load_new_report:
            mock_get_status.return_value = [None, None, 1, 'my_path']
            mock_load_new_report.return_value = 'load_new_report()'
            result = check_report_state(2023, 1, warned=True, use_current=False, mode='load', file=None,
                pract_data=None)
            assert result == 'load_new_report()'

    # def test_B6_7_positive_check_report_state(self):
    # with patch('report_status.get_status') as mock_get_status, patch(
    # 'funcs.load_new_report') as mock_load_new_report:
    # mock_get_status.return_value = [None, None, 1, 'my_path']
    # mock_load_new_report.return_value = 'load_new_report()'
    # result = check_report_state(2023, 1, warned=False, use_current=False, mode='load', file=None,
    # pract_data=None)  # assert result == 'load_new_report()'


class TestGenerateReport(unittest.TestCase):
    def test_B6_8_positive_generate_report(self):
        with patch('curriculum_getter.get_curriculum_data') as mock_get_curriculum_data,\
                app.app_context():
            mock_get_curriculum_data.return_value = {'22307': 'учебно-ознакомительная'}
            result = generate_report(2023, 1)
            assert isinstance(result, flask.wrappers.Response)
            # groups = json.load(result)
            assert result.status_code == 200
            assert b'practice info needed' in result.data

    def test_B6_9_positive_generate_report(self):
        with patch('curriculum_getter.get_curriculum_data') as mock_get_curriculum_data,\
                patch('report_generator.report') as mock_report,\
                app.app_context():
            mock_get_curriculum_data.return_value = None
            mock_report.return_value = True
            result = generate_report(2023, 1,
                                     pract_data={22202: 'учебно-ознакомительная',
                                                 22203: 'учебно-ознакомительная',
                                                 22404: 'производственная'})
            assert 'Второе состояние страницы' in result
            assert 'Year = 2023, Semester = 1' in result
            assert funcs.current_file_path == 'doc/1_2023-2024'


class TestLoadNewReport(unittest.TestCase):
    def test_B6_10_positive_load_new_report(self):
        pass

    def test_B6_12_negative_load_new_report(self):
        pass


class TestLoadChangedReport(unittest.TestCase):
    def test_B6_11_positive_load_changed_report(self):
        pass

    def test_B6_13_negative_load_changed_report(self):
        pass


class TestGeneratePdfFileAndUpload(unittest.TestCase):
    current_file_path = 'doc/report.doc'

    @patch('builtins.open')
    def test_B6_14_positive_generate_pdf_file_and_upload(self, mock_open):
        with patch('report_status.set_status') as mock_set_status,\
                patch('os.path.exists') as mock_exists,\
                patch('os.path.isfile') as mock_isfile,\
                patch('os.path.getsize') as mock_getsize,\
                patch('requests.post') as mock_post,\
                patch('docx2pdf.convert') as mock_convert,\
                app.app_context():
            funcs.current_file_path = 'doc/report.doc'
            mock_exists.return_value = True
            mock_isfile.return_value = True
            mock_getsize.return_value = 1
            mock_set_status.return_value = True
            mock_convert.return_value = None
            mock_response = mock_post.return_value
            mock_response.status_code = 200
            mock_response.json.return_value = {'result': 'success'}
            mock_file = mock_open.return_value
            mock_file.read.return_value = 'Mocked file content'
            result = generate_pdf_file_and_upload(2023, 1)
            assert isinstance(result, flask.wrappers.Response)
            assert result.status_code == 200
            # b = bytes("success:true")
            # assert b"true" in result.data
            decoded = result.data.decode('utf-8')
            data = json.loads(decoded)
            assert data['success'] is True
            assert "Итоговый отчёт успешно сформирован и добавлен на сервер ИМИТ" in data['message']
            mock_open.assert_called_once_with('doc/report.pdf', 'rb')


if __name__ == '__main__':
    unittest.main()
