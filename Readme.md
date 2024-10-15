### Unregistered User Authorization Model Description

- Access tokens are issued for each interaction with the server by an unregistered user. For example, when adding an order or clicking the mini-messenger button. The token's lifespan is 2 weeks. Each token creates a new WebUsers user without a profile and access to the site.
- The app_auth section contains static JavaScript code that adds authorization to the base template.


### Парсеры
- Парсеры работают постоянно и жрут примерно 1 гиг оперативки.
- Мысль Дня. Надо переписать на селери и включать только когда действительно нужно. Например, когда добавляется заказ или когда пользователь заходит на страницу с товарами.Плюс нам не нужно 4 селениму однавременно поддерживать.

### Мысли
https://drive.google.com/file/d/1yezIh0CK7UqjQRVVkNU_svJv486CTKAE/view?usp=sharing

### Authorization 
- django EmailVerificationRequiredMixin,ActiveUserConfirmMixin
- токен в куку app_auth/static/js/token_auth.js
# Orders Body Example
### Register orders
```python
{"country":"Greate Britain",
 "items":{"1":{"url":"https://thomasfarthing.co.uk... ","amount":1,"comment":"Цвет - GREY, размер - 40/31\""},
          "2":{"url":"https://thomasfarthing.co.uk/pr...","amount":1,"comment":"Цвет - BROWN, размер - 58cm"}
          },
 "username":"shangrila",
 "phone_number":"+79113613029",
 "cdek_adress":"180017, Россия, Псковская область, Псков, ул. Яна Фабрициуса, 10Е."}
```
### Unregister orders
```python
{"country":"europe",
 "url":"https://www.summitracing.com/parts/arb-3426050",
 "price":"1000",
 "comment":"Бампер",
 "email":"akhmiev88@mail.ru",
 "phone":"87018022228",
 "username":"UNREG_s5xMYZBpVqYsG0ISpgFN",
 "user_ip":"2.73.21.175"}
```
- Так выглядят заказы которые обрабатывает бот. Что бы изменить схему необходимо будет все элементы handlers адаптировать под новую схему.
- Solution: Добавлю на сервер 2 функции которые будут ухудшать ситуацию и паристь нормальный словарь в кривой json.