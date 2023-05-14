import re

from autoreport_config import CONFIG_PLAN_FILES_PATH
from docx2pdf import convert
from flask import send_from_directory, jsonify, render_template
import requests

import curriculum_getter
import report_generator
import report_state

current_file_path = ""


def generate_report_name(year: int, semester: int):
    """
    Генерация имени отчёта по определённому шаблону.

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.

    @return: Новое название файла.
    """
    years = f'{year}-{year + 1}' if semester == 1 else f'{year - 1}-{year}'
    return f'{semester}_{years}'


def update_curriculum():
    """
    Обрабатывает запрос пользователя на обновление учебной информации в базе данных.

    @return: json.
    """
    pattern = r'/.*config\.txt$'
    match = re.search(pattern, CONFIG_PLAN_FILES_PATH)
    if not match:
        return jsonify(
            {"success": False, "errortype": "config file access", "message": "Не найден конфигурационный файл."})
    try:
        with open(CONFIG_PLAN_FILES_PATH, "r") as file:
            for line in file:
                # TODO return curriculum_importer.py:insertInDataBase(line)
                pass
    except FileNotFoundError:
        return jsonify(
            {"success": False, "errortype": "config file access", "message": "Не найден конфигурационный файл."})


def generate_pdf_file_and_upload():
    """
    Генерация итогового отчёта (в формате .pdf) и его загрузка на сайт ИМИТ'а.

    @return: json / render_template().
    """
    global current_file_path

    # TODO: check current_file_path

    new_pdf_name = current_file_path[:current_file_path.rfind('.')] + '.pdf'

    convert(current_file_path, new_pdf_name)

    # TODO: check pdf file

    # TODO: url
    url = '/fm/add'

    data = {}

    file = {'file': open(new_pdf_name, 'rb')}

    response = requests.post(url, data=data, files=file)

    if response.status_code == 200:
        # TODO: return something good
        pass
    else:
        # TODO: return something bad
        pass


def check_report_state(year: int, semester: int, mode: str, warned=False, use_current=False, file=None,
        pract_data=None):
    """
    Проверка состояния отчёта за year год и semester семестр.

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.
    @param mode: Режим работы: загрузка или генерация.
    @param warned: Флаг для определения ответа пользователя на предупреждение; если warned = True - значит пользователь предупреждён и всё равно хочет продолжить.
    @param use_current: Флаг для определения ответа пользователя на предупреждение; если use_current = True - значит пользователь хочет использовать уже существующий отчёт в формате .doc.
    @param file: Файл, загруженный пользователем (для загрузки отчёта).
    @param pract_data: Информация о практиках, введённая пользователем.

    @return: json / render_template().
    """

    def handle_load_or_save(mode, year, semester, file=None, pract_data=None):
        if mode == 'load':
            return load_new_report(year, semester, file)
        elif mode == 'save':
            return generate_report(year, semester, pract_data)

    report_record = report_state.get_status(year, semester)

    if report_record is None:
        return handle_load_or_save(mode, year, semester, file, pract_data)
    else:
        report_state = report_record[3]

        if report_state == 0 and use_current:
            global current_file_path
            current_file_path = report_record[4]
            return render_template('second_state.html', year=report_record[1], semester=report_record[2])
        elif (report_state == 0 or report_state == 1) and warned:
            return handle_load_or_save(mode, year, semester, file, pract_data)
        elif report_state == 0:
            return jsonify({"success": False, "errortype": "report has state 0",
                "message":             "Данный отчёт уже был сформирован. Сформировать новый или использовать текущий?",
                "buttons":             {"first": "Новый", "second": "Текущий"}})
        elif report_state == 1:
            return jsonify({"success": False, "errortype": "report has state 1",
                "message":             "Данный отчёт уже был добавлен на сервер. Сформировать заново?",
                "buttons":             {"first": "Нет", "second": "Да"}})


def generate_report(year, semester, pract_data=None):
    """
    Формирование отчёта в формате .doc.

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.
    @param pract_data: Информация о практиках, введённая пользователем.

    @return: json / render_template().
    """
    if pract_data is None:
        groups = curriculum_getter.get_curriculum_data(year, semester, only_pract=True)
        return jsonify({"success": False, "errortype": "practice info needed", "groups": groups})
    else:
        curriculum_data = curriculum_getter.get_curriculum_data(year, semester)  # TODO: check curriculum_data
        report_path = 'doc/' + generate_report_name(year, semester)
        if report_generator.report(year, semester, report_path, curriculum_data, pract_data):
            global current_file_path
            current_file_path = report_path
            report_state.set_status(year, semester, 0, report_path)
            return render_template('second_state.html', year=year, semester=semester)
        else:
            return jsonify(
                {"success": False, "errortype": "report generation", "message": "Ошибка при формировании отчёта"})


def load_new_report(year, semester, file):
    """
    Сохранение загруженного пользователем отчёта в формате .doc.

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.
    @param file: Файл, загруженный пользователем.

    @return: json / render_template().
    """
    pass


def load_changed_report(year, semester, file):
    """
    Сохранение загруженного пользователем отчёта в формате .doc (после локального редактирования).

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.
    @param file: Файл, загруженный пользователем.

    @return: json.
    """
    pass


def download_report():
    """
    Скачивание пользователем отчёта для редактирования.

    @return: send_from_directory().
    """
    global current_file_path
    # FIXME: security warning on using 'send_from_directory' function
    return send_from_directory(directory='doc', path=current_file_path, as_attachment=True, mimetype='application/pdf')
