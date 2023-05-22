#from flask import Blueprint, Flask
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

year = None
term = None
user_year = None
data = None
type_report = None
name_report = None

@app.route('/', methods=["POST", "GET"])
def index():
    """
    Взаимосвязь между клиентской частью и модулем funcs.py.
    Обрабатывает POST запросы, отправленные с клиентской части
    Работает с элементами Главной страницы

    @return: вызов функций или render_template('main.html')
    """
    global year, term, type_report, name_report
    if request.method == 'POST':
        values = request.form.get('type')
        if values == 'upload':
            #return update_curriculum()
            return jsonify({"success": False, "errortype": "db no connection", "message": "Нет ответа от базы данных."})
        elif values == 'report':
            type_report = "gen"
            year = request.form.get('year')
            term = request.form.get('term')
            # pract = generate_report(year, term)
            return jsonify({"22102": "учебная", "22202": "производственная", "22301": "учебно-ознакомительная", "22303": "учебно-ознакомительная", "22305": "учебно-ознакомительная"})
        elif values == 'gen_report':
            pract = request.form.get('pract')
            # return generate_report(year, term, pract)
            return render_template("report.html", type_report=type_report, name_report=name_report)
        elif values == 'report_upload':
            print("Загрузка отчёта")
            type_report = "upload"
            file = request.form.get('file')
            # return load_new_report(year, term, file)
            return render_template("report.html", type_report=type_report, name_report=name_report)
        
    return render_template('main.html')

@app.route('/report', methods=["POST", "GET"])
def web_report():
    """
    Взаимосвязь между клиентской частью и модулем funcs.py.
    Обрабатывает POST запросы, отправленные с клиентской части
    работает с элементами страницы отчёта

    @return: вызов функций или render_template('main.html')
    """
    global year, term, type_report, name_report
    if request.method == 'POST':
        print("post")
        values = request.form.get('type')
        if values == 'download_report':
            # return download_report()
        elif values == 'upload_report':
            file = request.form.get('file')
            # return load_changed_report(year, term, file)
        elif values == 'add_report':
            # return generate_pdf_file_and_upload()
    return render_template('report.html')

# autoreport = Blueprint('autoreport', __name__, template_folder='templates', static_folder='static')

