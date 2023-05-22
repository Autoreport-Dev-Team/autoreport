
function find_date(){
    //
    // Заполняет список годов элементами
    //
    var select = document.getElementById("user_year");
    let year = new Date();
    let date = year.getFullYear();

    for (var i = 0; i < 6; ++i) {
        var el = document.createElement("option");
        el.text = Number(date)-i;
        el.value = Number(date)-i;

        select.add(el);
    }
}
function hide_pop_up_window(event) {
    //
    // Скрывает всплывающее окно
    //
    document.getElementById('modal').style.display = 'none';
    document.getElementById('window_1_modal').style.display = 'none';

}

function hide_pop_up_window_pract(event, window) {
    //
    // Скрывает диалоговое окно
    //
    document.getElementById('modal').style.display = 'none';
    document.getElementById('window_3_modal').style.display = 'none';

}

function fill_practic(array_practic_one) {
    //
    // Заполняет диалоговое окно данными о практике и элементами для дополнения данных о практиках
    //
    // @params pract: массив с данными о практиках
    //
    document.getElementById('modal').style.display = 'flex';
    document.getElementById('window_3_modal').style.display = 'flex';

    str_1 = ""
    str_2 = ""
    str_3 = ""
    str_4 = ""
    
    array_practic_one.forEach(element => {
        if (element[0][2] == '1'){
            str_1 = str_1 + '<p class="pract_text">' + element[0] + '</p><p class="pract_text">' + element[1] + '</p><div><input type="text" class="textbox" id="textbox_time_' + element[0] + '"></div><div><input type="text" class="textbox" id="textbox_name_' + element[0] + '"></div><div><button class="delete"></button></div>'
        }
        if (element[0][2] == '2'){
            str_2 = str_2 + '<p class="pract_text">' + element[0] + '</p><p class="pract_text">' + element[1] + '</p><div><input type="text" class="textbox" id="textbox_time_' + element[0] + '"></div><div><input type="text" class="textbox" id="textbox_name_' + element[0] + '"></div><div><button class="delete"></button></div>'
        }
        if (element[0][2] == '3'){
            str_3 = str_3 + '<p class="pract_text">' + element[0] + '</p><p class="pract_text">' + element[1] + '</p><div><input type="text" class="textbox" id="textbox_time_' + element[0] + '"></div><div><input type="text" class="textbox" id="textbox_name_' + element[0] + '"></div><div><button class="delete"></button></div>'
        }
        if (element[0][2] == '4'){
            str_4 = str_4 + '<p class="pract_text">' + element[0] + '</p><p class="pract_text">' + element[1] + '</p><div><input type="text" class="textbox" id="textbox_time_' + element[0] + '"></div><div><input type="text" class="textbox" id="textbox_name_' + element[0] + '"></div><div><button class="delete"></button></div>'
        }

    });

    kurs_1 = document.getElementById('kurs_1');
    kurs_1.innerHTML = str_1;

    kurs_2 = document.getElementById('kurs_2');
    kurs_2.innerHTML = str_2;

    kurs_3 = document.getElementById('kurs_3');
    kurs_3.innerHTML = str_3;

    kurs_4 = document.getElementById('kurs_4');
    kurs_4.innerHTML = str_4;
}

function pop_up_window(message) {
    //
    // Отображает всплывающее окно
    //
    // @params message: сообщение для отображения
    //
    document.getElementById('modal').style.display = 'flex';
    document.getElementById('window_1_modal').style.display = 'flex';

    str_window_message = '<p>' + message + '</p>'
    console.log(str_window_message)
    window_message = document.getElementById('window_message');
    window_message.innerHTML = str_window_message;
}
function find_db(event){
    //
    // Создает POST запрос для кнопки "Обновить данные об учебных планах"
    //
      document.querySelector('#form').onsubmit = () => {

          // Инициализировать новый запрос
          const request = new XMLHttpRequest();
          request.open('POST', '/');

          // Функция обратного вызова, когда запрос завершен
          request.onload = () => {

              // Извлечение данных JSON из запроса
              const data = JSON.parse(request.responseText);
              pop_up_window(data['message'])

          }

          // Добавить данные для отправки с запросом
          const type = new FormData();
          type.append('type', 'upload');

          // Послать запрос
          request.send(type);
          return false;
      };
  }

function find_practic(event){
    //
    // Создает POST запрос для кнопки "Сформировать отчёт" для получения данных о практиках из бд
    //
      document.querySelector('#form').onsubmit = () => {

          // Инициализировать новый запрос
          const request = new XMLHttpRequest();
          request.open('POST', '/');

          // Функция обратного вызова, когда запрос завершен
          request.onload = () => {

              // Извлечение данных JSON из запроса
              const data = JSON.parse(request.responseText);
              var result = new Array;
              for(var i in data)
                result.push([i, data[i]]);
              fill_practic(result)

          }

          // Добавить данные для отправки с запросом
          x = document.getElementById('user_term').value
          y = document.getElementById('user_year').value
          const type = new FormData();
          type.append('type', 'report');
          type.append('user_year', String(y));
          type.append('user_term', String(x));

          // Послать запрос
          request.send(type);
          return false;
      };
  }

function find_report(event){
    //
    // Создает POST запрос для кнопки "Готово" для дальнейшего формирования отчёта
    // 
    
    // тут будет функция!
  }
