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

## Базы данных
### Для создания базы данных, необходимой для хранения данных из учебных планов и данных об отчётах на сервисе, требуется выполнить следующие SQL-запросы в СУБД (MariaDB):
1. Для создания пустой базы данных c именем db:
```
CREATE DATABASE `db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */
```

2. Для создания таблицы tbl_subjects, хранящей информацию о учебных дисциплинах: 
```
  CREATE TABLE `tbl_subjects` (
    `subjectId` int(11) NOT NULL AUTO_INCREMENT,
    `subjectName` varchar(200) NOT NULL,
    `accred` varchar(12) NOT NULL,
    `semester` tinyint(1) DEFAULT NULL,
    `pract` tinyint(1) DEFAULT NULL,
    PRIMARY KEY (`subjectId`),
    UNIQUE KEY `tbl_subjects_un` (`semester`,`accred`,`subjectName`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

3. Для создания таблицы tbl_directions, хранящей информацию о направлениях подготовки:
```
  CREATE TABLE `tbl_directions` (
    `dirId` int(11) NOT NULL AUTO_INCREMENT,
    `dirName` varchar(50) DEFAULT NULL,
    `adyear` int(11) NOT NULL,
    PRIMARY KEY (`dirId`),
    UNIQUE KEY `dirName` (`dirName`,`adyear`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

4. Для создания таблицы tbl_links, хранящей информацию о связях учебных дисциплин и направлений подготовки:
```
  CREATE TABLE `tbl_links` (
    `linkId` int(11) NOT NULL AUTO_INCREMENT,
    `dirId` int(11) NOT NULL,
    `subjectId` int(11) NOT NULL,
    PRIMARY KEY (`linkId`),
    UNIQUE KEY `tbl_links_un` (`dirId`,`subjectId`),
    KEY `subjectData` (`subjectId`),
    CONSTRAINT `dirData` FOREIGN KEY (`dirId`) REFERENCES `tbl_directions` (`dirId`),
    CONSTRAINT `subjectData` FOREIGN KEY (`subjectId`) REFERENCES `tbl_subjects` (`subjectId`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

5. Для создания таблицы tbl_reports, хранящей информацию о состоянии отчёта:
```
  CREATE TABLE `tbl_reports` (
    `repId` int(11) NOT NULL,
    `repYear` int(11) DEFAULT NULL,
    `repSem` int(11) DEFAULT NULL,
    `repStatus` tinyint(1) DEFAULT NULL,
    `repPath` varchar(1000) DEFAULT NULL,
    PRIMARY KEY (`repId`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

6. Для того чтобы сервис мог работать с созданной базой данных, в конфигурационном файле config.py параметры для соединения: 
```
    user - имя пользователя
    password - пароль пользователя
    host - IP-адрес для подключения (по умолчанию localhost)
    port - порт для подключения (по умолчанию 3306)
```