from telebot import types


def get_types_markup():
    types_murkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    types_but1 = types.KeyboardButton('Фильм')
    types_but2 = types.KeyboardButton('Сериал')
    types_but3 = types.KeyboardButton('Мультфильм')
    types_but4 = types.KeyboardButton('Аниме')
    types_murkup.add(types_but1, types_but2, types_but3, types_but4)
    return types_murkup


def get_start_markup():
    start_murkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    start_but1 = types.KeyboardButton("Поиск фильма/сериала по названию")
    start_but2 = types.KeyboardButton("Поиск фильмов/сериалов по рейтингу")
    start_but3 = types.KeyboardButton("Поиск фильмов/сериалов по типу")
    start_but4 = types.KeyboardButton("Поиск фильмов/сериалов по жанру")
    start_but5 = types.KeyboardButton("История запросов")
    start_murkup.add(start_but1, start_but2, start_but3, start_but4, start_but5)
    return start_murkup


def get_genre_markup():
    genre_murkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    genre_but1 = types.KeyboardButton('Комедия')
    genre_but2 = types.KeyboardButton('Драма')
    genre_but3 = types.KeyboardButton('Ужасы')
    genre_but4 = types.KeyboardButton('Боевик')
    genre_murkup.add(genre_but1, genre_but2, genre_but3, genre_but4)
    return genre_murkup
