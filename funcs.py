from autoreport_config import CONFIG_PLAN_FILES_PATH
from docx2pdf import convert
from flask import send_from_directory
import requests

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
    with open(CONFIG_PLAN_FILES_PATH, "r") as file:
        for line in file:
            # TODO curriculum_importer.py:insertInDataBase(line)
            pass


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


def check_report_state(year: int, semester: int, mode: str, warned=False, use_current=False, file=None, pract_data=None):
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
    pass


def generate_report(year, semester, pract_data=None):
    """
    Формирование отчёта в формате .doc.

    @param year: Год, за который сформирован/загружен отчёт.
    @param semester: Семестр, за который сформирован/загружен отчёт.
    @param pract_data: Информация о практиках, введённая пользователем.

    @return: json / render_template().
    """
    pass


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
