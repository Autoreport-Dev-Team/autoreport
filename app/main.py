from flask import Flask, render_template, request
from flask import send_from_directory, flash
from datetime import date
from docx import Document
from flask import redirect, url_for
from htmldocx import HtmlToDocx
from collections import defaultdict
import mariadb
import sys
import os
import unittest
import webbrowser

from werkzeug.utils import secure_filename
from coverage import coverage

UPLOAD_FOLDER = 'doc'
ALLOWED_EXTENSIONS = {'doc'}

app = Flask(__name__, template_folder='../templates')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

year = None
term = None
path = None
user_year = None
nameFile = None
data = None


@app.route('/', methods=["POST", "GET"])
def index():
    global year, term, data
    data = int(str(date.today()).split("-")[0])
    if request.method == 'POST':
        year = request.form['user_year']
        term = request.form['user_term']
        return redirect(url_for('fileName'))
    return render_template('main.html', data=data)


@app.route('/main/', methods=["POST", "GET"])
def fileName():
    global year, term, path, nameFile, data

    if request.method != 'POST':
        nameFile = report(year, term)
        return render_template('main.html', fileName='doc/' + nameFile, data=data, x=True)

    # загрузка файла на пк
    if request.method == 'POST' and request.form['submit_button'] == "Скачать отчёт":
        return send_from_directory(directory='doc', path=nameFile, as_attachment=True, mimetype='application/pdf')

    elif request.method == 'POST' and request.form['submit_button'] == "Загрузить":
        filename = upload_file(request)
        return render_template('main.html', fileName=filename, data=2022, x=True)

    elif request.method == 'POST' and request.form['submit_button'] == "Посмотреть отчёт":
        filename = upload_file(request)
        return render_template('main.html', fileName=filename, data=2022, x=True)

def openFile():
    new = 2
    url = "app/doc/1.html"
    webbrowser.open(url, new=new)

# Функция проверки расширения файла
# Получает название файла, возвращает true, если
# расширение допустимо, иначе false
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Функция добавления загружаемого файла в папку AutoReport
# На вход получает данные с html
# Возвращает имя файла в случае успеха, иначе пустую строку
def upload_file(request):
    if 'file' not in request.files:
        flash('Не могу прочитать файл')
        return "Не получилось загрузить файл"
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename


# Функция составления отчета в формате doc
# Получает год и семестр в виде строки
# Возвращает имя отчета
def report(yearString, termString):
    if (yearString is None) or (termString is None):
        return False
    year = int(yearString)

    if termString == "весенний":
        term = 2
    else:
        term = 1

    groups = db(term)

    # модуль ссоставления отчетности
    document = Document()
    new_parser = HtmlToDocx()

    # Определение временного промежутка(годов)
    year = str(year) + '-' + str(year + 1)

    # Начало документа
    html = '<h1>Формы отчетности студентов за '+str(term) + ' семестр ' + year + ' уч.г.</h1><br>'

    # Общие строки в документе для всех групп
    tblstart = '<table border="1">'
    tblend = '</table>'
    tblhead = '<tr><td><b>Экзамены</b></td><td><b>Зачеты</b></td></tr>'

    # Добавление в документ таблицы групп
    for numberGroup in groups:
        strgroup = '<h2>Гр. '+str(numberGroup) + '</h2>'
        strr = strgroup + tblstart + tblhead
        for group in groups[numberGroup]:
            lenExam = len(group['exam'])
            lenCredit = len(group['credit'])

            for x in range(0, max(lenExam, lenCredit)):
                if x < lenExam:
                    exam = group['exam'][x]
                    exam = exam[0]
                else:
                    exam = ""

                if x < lenCredit:
                    credit = group['credit'][x]
                    credit = credit[0]
                else:
                    credit = ""

                strr = strr + '<tr><td>' + exam + '</td>' + '<td>' + credit + '</td></tr>'
        strr = strr + tblend
        html = html + strr + '<br>'

    new_parser.add_html_to_document(html, document)

    f = open('static/1.txt', 'w')
    f.write(html)
    f.close()
    nameFile = 'student_reporting_' + str(year) + '_' + str(term) + '_semester.doc'
    # path = 'doc/student_reporting_' + str(year)
    # + '_' + str(term) + '_semester.doc'
    document.save('doc/' + nameFile)
    return nameFile


# Функция получения данных из бд
# Получает семестр в int
# Возвращает лист groups со всеми данными для отчета
def db(term):
    try:
        conn = mariadb.connect(user="root", password="lizliz31415", host="127.0.0.1", port=3476, database="AuthoReport")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cur = conn.cursor()

    # Получение данных о группах
    cur.execute("SELECT * FROM tbl_groups;")
    rows = cur.fetchall()

    # Создание листа, который будет хранить данные,
    # передающиеся в модуль отчетности
    groups = defaultdict(list)

    # Заполнение листа groups  данными о экзаменах и зачетах
    for row in rows:
        id_group = row[1]
        kurs = row[0] * 2
        numbergroup = row[1]
        if term == 1:
            kurs = kurs - 1
        cur.execute("SELECT nameSubject FROM tbl_link, tbl_subjects where id_group = " + str(
            id_group) + " and tbl_link.id_subject = tbl_subjects.id_subject and (exam = " + str(kurs) + ");")
        subjectsExam = cur.fetchall()

        cur.execute("SELECT nameSubject, diff, elective FROM tbl_link, tbl_subjects where id_group = " + str(
            id_group) + " and tbl_link.id_subject = tbl_subjects.id_subject and (credit = " + str(kurs) + ");")

        arraysubjectsCredit = cur.fetchall()
        subjectsCredit = defaultdict(list)
        i = 0
        for credit in arraysubjectsCredit:
            if not (credit[2] is None) and (credit[2] == 1):
                cred = credit[0].split("/")
                s = "Дисциплина по выбору: " + cred[0] + " или " + cred[1]
            else:
                s = credit[0]
            if not (credit[1] is None) and (credit[1] == 1):
                s = s + "(оценка)"

            subjectsCredit[i].append(s)
            i = i + 1

        subject = {'exam': subjectsExam, 'credit': subjectsCredit}
        groups[numbergroup].append(subject)

    return groups


cov = coverage(branch=True)
cov.start()


class TestDef(unittest.TestCase):

    def test_report(self):
        year1 = "2020"
        term1 = "весенний"
        self.assertEqual(report(year1, term1), "student_reporting_2020-2021_2_semester.doc", "Should be file name")

    def test_report_neg(self):
        self.assertEqual(report("2020", None), False, "Should be false")

    def test_allowed_file(self):
        self.assertEqual(allowed_file("text.doc"), True, "Should be true")

    def test_allowed_file_neg(self):
        self.assertEqual(allowed_file("text.txt"), False, "Should be false")


# def report_neg(self):
#   self.assertEqual(upload_file(), False, "Should be false")


if __name__ == "__main__":
    #app.secret_key = os.urandom(24)
    #try:
    #    unittest.main()
    #except Exception:
    #    pass
    #cov.stop()
    #cov.save()
    #print("\n\nCoverage Report:\n")
    #cov.report()
    #print("HTML version: " + os.path.join("static", "index.html"))
    #cov.html_report(directory='static')
    #cov.erase()
    app.run(debug=True)
