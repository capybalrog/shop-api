# Shop API

## Основные функции:
- Категории и подкатегории товаров
- Информация о продуктах с изображениями
- Корзина покупок
- Аутентификация по токену
- Постраничный вывод данных
- Поиск и фильтрация
- Документация - Swagger/Redoc для API:
  - http://127.0.0.1:8000/redoc/
  - http://127.0.0.1:8000/swagger/ 

## Установка и запуск

1. Клонировать репозиторий
2. Перейти в папку `shop`: `cd shop`
3. Создать виртуальное окружение `python -m venv env`
4. Активировать виртуальное окружение `source env/bin/aсtivate`
5. Установить зависимости: `pip install -r requirements.txt`
6. Создать базу данных и настроить переменные окружения, как в файле `.env.example`:
7. Применить миграции: `python manage.py migrate`
8. Загрузить тестовые данные в базу: `python manage.py loaddata fixtures.json`
9. Создать суперпользователя для работы с админкой: `python3 manage.py createsuperuser`
10. Запустить сервер: `python manage.py runserver`
   Приложение будет доступно по адресу: http://127.0.0.1:8000/

## API Endpoints

### Аутентификация
- POST /api/auth/token/login/ - получение токена
- POST /api/auth/token/logout/ - выход

### Пользователи
- POST /api/users/ - регистрация нового пользователя

### Категории
- GET /api/categories/ - список всех категорий
- GET /api/categories/{slug}/ - категория с подкатегориями
- GET /api/categories/{category_slug}/{subcategory_slug}/ - продукты подкатегории

### Продукты
- GET /api/products/ - список всех продуктов
- GET /api/products/{slug}/ - детали продукта
- POST /api/products/{slug}/to_cart/ - добавить в корзину
- DELETE /api/products/{slug}/to_cart/ - удалить из корзины

### Корзина
- GET /api/cart/ - просмотр корзины
- PUT /api/cart/{item_id}/ - изменить количество
- DELETE /api/cart/{item_id}/ - удалить товар
- DELETE /api/cart/clear/ - очистить корзину

## Запуск тестов
- cd shop (корень проекта)
- python -m pytest