import os
import re

import flask

import curriculum_importer
from autoreport_config import CONFIG_PLAN_FILES_PATH
import docx2pdf
from flask import jsonify, render_template, send_file
import requests

import curriculum_getter
import report_generator
import report_status

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
                return curriculum_importer.insertInDataBase(line)
    except FileNotFoundError:
        return jsonify(
            {"success": False, "errortype": "config file access", "message": "Не найден конфигурационный файл."})


def generate_pdf_file_and_upload(year: int, semester: int):
    """
    Генерация итогового отчёта (в формате .pdf) и его загрузка на сайт ИМИТ'а.

    @return: json / render_template().
    """
    global current_file_path

    if current_file_path == '' or not os.path.exists(current_file_path):
        return jsonify({"success": False, "errortype": "wrong current file path", "message": "Отчёт не найден."})

    new_pdf_name = current_file_path[:current_file_path.rfind('.')] + '.pdf'

    docx2pdf.convert(current_file_path, new_pdf_name)

    if os.path.isfile(new_pdf_name) and os.path.getsize(new_pdf_name) > 0:
        file_ext = os.path.splitext(new_pdf_name)[1]
        if file_ext == '.pdf':
            pass
        else:
            return jsonify({{"success": False, "errortype": "report convert",
                            "message": "Произошла ошибка при конвертации .pdf отчёта."}})
    else:
        return jsonify({{"success": False, "errortype": "report convert",
                        "message": "Произошла ошибка при конвертации .pdf отчёта."}})

    url = 'https://imit.petrsu.ru/fm/add'

    data = {}

    file = {'file': open(new_pdf_name, 'rb')}

    response = requests.post(url, data=data, files=file)

    if response.status_code == 200 and response.json().get("result") == "success":
        if not report_status.set_status(year, semester, 1, new_pdf_name):
            return jsonify({"success": False, "errortype": "db no connection", "message": "Нет ответа от базы данных."})
        else:
            return jsonify({"success": True,
                            "message": "Итоговый отчёт успешно сформирован и добавлен на сервер ИМИТ."})
    else:
        return jsonify({"success": False, "errortype": "adding pdf to IMIT",
                        "message": "Ошибка при добавлении итогового отчёта на сервер ИМИТ."})


def check_report_state(year: int, semester: int, mode: str, warned=False, use_current=False, file=None,
                       pract_data=None):
    """
    Проверка состояния отчёта за year год и semester семестр.

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.
    @param mode: Режим работы: загрузка или генерация.
    @param warned: Флаг для определения ответа пользователя на предупреждение; если warned = True - значит пользователь
    предупреждён и всё равно хочет продолжить.
    @param use_current: Флаг для определения ответа пользователя на предупреждение; если use_current = True - значит
    пользователь хочет использовать уже существующий отчёт в формате .doc.
    @param file: Файл, загруженный пользователем (для загрузки отчёта).
    @param pract_data: Информация о практиках, введённая пользователем.

    @return: json / render_template().
    """

    def handle_load_or_save(mode, year, semester, file=None, pract_data=None):
        if mode == 'load':
            return load_new_report(year, semester, file)
        elif mode == 'save':
            return generate_report(year, semester, pract_data)

    report_record = report_status.get_status(year, semester)

    if isinstance(report_record, flask.wrappers.Response):
        return report_record
    elif report_record is None:
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
                            "message": "Данный отчёт уже был сформирован. Сформировать новый или использовать текущий?",
                            "buttons": {"first": "Новый", "second": "Текущий"}})
        elif report_state == 1:
            return jsonify({"success": False, "errortype": "report has state 1",
                            "message": "Данный отчёт уже был добавлен на сервер. Сформировать заново?",
                            "buttons": {"first": "Нет", "second": "Да"}})


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

        if isinstance(groups, flask.wrappers.Response):
            return groups

        return jsonify({"success": False, "errortype": "practice info needed", "groups": groups})
    else:
        curriculum_data = curriculum_getter.get_curriculum_data(year, semester)

        if isinstance(curriculum_data, flask.wrappers.Response):
            return curriculum_data

        report_path = 'doc/' + generate_report_name(year, semester)

        if report_generator.report(year, semester, report_path, curriculum_data, pract_data):
            report_status.set_status(year, semester, 0, report_path)
            global current_file_path
            current_file_path = report_path
            return render_template('second_state.html', year=year, semester=semester)
        else:
            return jsonify({"success": False, "errortype": "report generation",
                            "message": "Ошибка при формировании отчёта"})


def load_new_report(year, semester, file):
    """
    Сохранение загруженного пользователем отчёта в формате .doc.

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.
    @param file: Файл, загруженный пользователем.

    @return: json / render_template().
    """
    global current_file_path
    report_path = 'doc/' + generate_report_name(year, semester)

    try:
        file.save(report_path)
        current_file_path = report_path

        if report_status.set_status(year, semester, 0, report_path):
            return render_template('second_state.html', year=year, semester=semester)
        else:
            return jsonify({"success": False, "errortype": "db no connection", "message": "Нет ответа от базы данных."})

    except Exception as e:
        return jsonify({"success": False, "errortype": "saving loaded file",
                        "message": "Отчёт не был сохранён.", "exception": type(e)})


def load_changed_report(year, semester, file):
    """
    Сохранение загруженного пользователем отчёта в формате .doc (после локального редактирования).

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.
    @param file: Файл, загруженный пользователем.

    @return: json.
    """
    global current_file_path

    if current_file_path == '':
        return jsonify({"success": False, "errortype": "wrong current file path", "message": "Отчёт не найден."})

    try:
        file.save(current_file_path)
        return render_template('second_state.html', year=year, semester=semester)
    except Exception as e:
        return jsonify({"success": False, "errortype": "saving loaded file",
                        "message": "Отчёт не был сохранён.", "exception": type(e)})


def download_report():
    """
    Скачивание пользователем отчёта для редактирования.

    @return: send_from_directory().
    """
    global current_file_path

    if current_file_path == '' or not os.path.exists(current_file_path):
        return jsonify({"success": False, "errortype": "wrong current file path", "message": "Отчёт не найден."})

    # FIXME: security warning on using 'send_from_directory' function
    return send_file(current_file_path, as_attachment=True, mimetype='application/doc')
