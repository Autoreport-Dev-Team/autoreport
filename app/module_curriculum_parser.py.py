# dbModule_v_0.4.py - модуль работы с учебными планами дирекции ИМИТ ПетрГУ
#
# 22/03/2023, Oleg Lisickii <lisickii@cs.karelia.ru>
#
# use it as you wish, pal

import xlrd
import os
import mariadb
import sys

# пробуем подключится к БД (данные с локальной бд)
try:
    conn = mariadb.connect(
        user="root",
        password="1024",
        host="localhost",
        port=3306,
        database="db"
    )

# если не удалось подключиться, кидаем ошибку
except mariadb.Error as e:
    print("Error occured during connection to db: {e}")
    sys.exit(1)

# установка, чтобы транзакции по соеднинению выполнялись сразу после их вызова автоматически
conn.autocommit = True

# открываем и считываем конфигурационный файл
if (os.path.isfile("config.txt")):
    configFile = open("config.txt", "r")
    planFiles = configFile.readlines()
    configFile.close()

    cur = conn.cursor()  # устанавливаем курсор для соединения (позволяет выполнять sql команды)

    # Залезаем в каждый учебный план, перечисленный в конфиге
    for fname in planFiles:
        fname = os.path.split(fname.strip())[1]

        book = xlrd.open_workbook(filename=fname)  # открываем таблицу эксель

        dirName = str(book.sheet_by_name(               # получаем код направления и год
            'УП').cell_value(2, 0)).split(" - ")[0]
        adyear = int(fname.split(".")[0].split("_")[2])

        # вставляем данные о направлении в таблицу БД, если их не было ранее; запоминаем Идентификатор направления
        data = (dirName, adyear)

        cur.execute(
            "INSERT INTO tbl_directions (dirName, adyear) VALUES (%s,%d) ON DUPLICATE KEY UPDATE dirId=dirId;", data)

        cur.execute(
            "SELECT dirId FROM tbl_directions WHERE dirName = %s and adyear = %d;", data)

        dirId = cur.fetchone()

        # функция для отправки данных предмета в БД
        def insertInDataBase(subjectName, accredType, semester, pract, accredCol):

            # проверяем наличие указанное типа аттестации в выбранном семестре; запоминаем Идентификатор предмета
            if (sh.cell_value(j, accredCol) != ''):

                # в таблицу БД с предметами вносится запись, если её не было ранее
                data = (subjectName, accredType, semester, pract)
                cur.execute(
                    "INSERT INTO tbl_subjects (subjectName, accred, semester, pract) VALUES (%s,%s,%d,%d) ON DUPLICATE KEY UPDATE subjectId=subjectId;", data)
                cur.execute(
                    "SELECT subjectId FROM tbl_subjects WHERE subjectName = %s and accred = %s and semester = %d and pract = %d", data)

                subjectId = cur.fetchone()

                # в таблицу БД со связями направление/предмет вносится запись с полученными Ид, если её не было ранее.
                data = (dirId[0], subjectId[0])

                cur.execute(
                    "INSERT INTO tbl_links (dirId, subjectId) VALUES (%d,%d) ON DUPLICATE KEY UPDATE linkId=linkId", data)

        # обход учебного план i-го курса
        for i in range(1, 6):
            shName = str(i) + '_курс'
            if (shName in book.sheet_names()):  # проверям, что такой лист есть в экселе
                sh = book.sheet_by_name(shName)

                for j in range(3, sh.nrows):
                    if (sh.cell_value(j, 1) != ""):

                        subjectName = sh.cell_value(j, 1)

                        # нахождение и связка дисциплин по выбору в пары
                        if ("Дисциплины по выбору" in sh.cell_value(j, 1)):
                            for l in reversed(range(j+1, sh.nrows)):
                                if (sh.cell_value(j, 1) == sh.cell_value(l, 1)):
                                    subjectName = str(sh.cell_value(
                                        l+1, 1)) + " или " + str(sh.cell_value(l+2, 1))

                        if ("практика" in str(sh.cell_value(j, 1))):
                            pract = True
                        else:
                            pract = False

                        # если дошли до конца
                        if (subjectName == "Итого"):
                            continue

                        for k in range(2):          # обход по семестру
                            sem = i*2 - 1 + k
                            exCol = 8 + k*10  # № колонка, в которой находятся метки об экзаменах
                            # следующие 2 колонки за ней -- для зачета и дифф зачета соотв.

                            insertInDataBase(
                                subjectName, "exam", sem, pract, exCol)
                            insertInDataBase(
                                subjectName, "cred", sem, pract, exCol + 1)
                            insertInDataBase(
                                subjectName, "diff", sem, pract, exCol + 2)
else:
    print("confing.txt not found")
conn.close()
