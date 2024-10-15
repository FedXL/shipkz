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