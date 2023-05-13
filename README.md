# AutoReport
AutoReport — сервис автоматизации формирования отчетов. Предоставляет пользователю возможность сформировать отчёт за выбранный год и семестр и загрузить его на сервер ИМИТ.

## Установка AutoReport в существующий проект в качестве подсистемы с использованием технологии Blueprint.
1. Выполнить clone репозитория в существующий проект:
```
cd web/imit
git clone https://github.com/Autoreport-Dev-Team/autoreport
```

2. Перейти в директорию проекта:
```
cd autoreport
```

3. Установить зависимости из requirements.txt:
```
pip3 install -r requirements.txt
```

4. В конфигурационном файле autoreport_config.py установить путь до файла с путями до файлов учебных планов:
```
CONFIG_PLAN_FILES_PATH = "path/to/config.txt"
```

5. Вернуться в директорию исходного проекта:
```
cd ..
```

6. В файле, где инициализируется экземпляр flask, импортировать autoreport:
```
from autoreport.autoreport import autoreport
```
И подключить подсистему autoreport к проекту:
```
app.register_blueprint(autoreport, url_prefix='/autoreport'
```