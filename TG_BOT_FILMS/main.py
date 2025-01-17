import datetime
import requests
import json
import time
import re
import os

from dotenv import load_dotenv
from peewee import IntegrityError
from telebot import StateMemoryStorage, TeleBot
from telebot.custom_filters import StateFilter
from telebot.handler_backends import State, StatesGroup
from telebot.types import BotCommand, Message, ReplyKeyboardRemove
from telebot import types

from keybords import get_types_markup, get_genre_markup, get_start_markup
from config import DEFAULT_COMMANDS
from models import history_films, User, create_models

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
X_API_KEY = os.getenv("X_API_KEY")

state_storage = StateMemoryStorage()

bot = TeleBot(BOT_TOKEN, state_storage=state_storage)

type_films = ""
genre_films = ""
global_count = 0


def data_reader(message, data, i=0):
    try:
        genres = list()
        name = data["docs"][i]["name"]
        if name is None:
            return False
        filmCritics = data["docs"][i]["rating"]["kp"]
        if data["docs"][i]["description"] is None:
            description = ""
        else:
            description = data["docs"][i]["description"]
        year = data["docs"][i]["year"]
        for genre in data["docs"][i]["genres"]:
            genres.append(genre["name"])
        if data["docs"][i]["ageRating"] is None:
            ageRating = "0+"
        else:
            ageRating = data["docs"][i]["ageRating"]
        if not "poster" in data["docs"][i] or data["docs"][i]["poster"]["url"] is None:
            poster = ""
        else:
            poster = data["docs"][i]["poster"]["url"]
        current_date = datetime.datetime.now()
        with bot.retrieve_data(message.from_user.id) as data:
            data["new_film"]["title"] = name
            data["new_film"]["description"] = description
            data["new_film"]["rating"] = filmCritics
            data["new_film"]["year"] = year
            data["new_film"]["genre"] = ", ".join(map(str, genres))
            data["new_film"]["age_rating"] = ageRating
            data["new_film"]["poster"] = poster
            data["new_film"]["due_data"] = current_date.strftime("%m/%d/%y %H:%M:%S")
    except KeyError:
        return False
    return data


class UserState(StatesGroup):
    """
    Класс, содержащий статусы
    """

    new_film_title = State()
    new_film_rating = State()
    new_film_search_by_type = State()
    new_film_genres = State()
    count = State()


@bot.message_handler(commands=["start"])
def handle_start(message: Message) -> None:
    """
    Функция обрабатывающая команду start, инициирующая пользователя и добавляющая Reply клавиатуру
    :param message:
    :return:
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    try:
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
        )
        start_murkup = get_start_markup()
        bot.reply_to(
            message,
            "Рад приветствовать! Я бот по поиску фильмов и сериалов, выберите следующее действие.",
            reply_markup=start_murkup,
        )
    except IntegrityError:
        start_murkup = get_start_markup()
        bot.reply_to(
            message,
            f"Рад вас снова видеть, {first_name}! Выберите следующее действие.",
            reply_markup=start_murkup,
        )


@bot.message_handler(state="*", commands=["movie_search"])
def choice_name(message: Message) -> None:
    """
    Функция обрабатывающая команду movie_search, запрашивает название фильма и обращается к базе данных чтобы в
    дальнейшем записать в нее информацию о фильме
    :param message:
    :return:
    """
    bot.send_message(message.from_user.id, "Введите название Фильма/Сериала")
    user_id = message.from_user.id
    bot.set_state(message.from_user.id, UserState.new_film_title)
    with bot.retrieve_data(message.from_user.id) as data:
        data["new_film"] = {"user_id": user_id}


@bot.message_handler(state=UserState.new_film_title)
def search_name(message: Message) -> None:
    """
    Функция создающая запрос API серверу для получения информации о фильме по названию и записывающая информацию в базу
    данных
    :param message:
    :return:
    """
    query = message.text.strip().lower()
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=1&query={query}"
    headers = {"accept": "application/json", "X-API-KEY": X_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        bot.send_message(
            message.from_user.id, "К сожалению произошла какая то ошибка😢"
        )
        bot.delete_state(message.from_user.id)
    try:
        data = json.loads(response.text)
        new_data = data_reader(message, data)
        new_film = history_films(**new_data["new_film"])
        new_film.save()
        bot.send_message(
            message.from_user.id,
            f"Название: {new_data["new_film"]["title"]}"
            f"\nОписание: {new_data["new_film"]["description"]}"
            f"\nРейтинг: {new_data["new_film"]["rating"]}"
            f"\nГод выпуска: {new_data["new_film"]["year"]}"
            f"\nЖанр: {new_data["new_film"]["genre"]}"
            f"\nВозрастной рейтинг: {new_data["new_film"]["age_rating"]}"
            f"\n{new_data["new_film"]["poster"]}",
        )
        bot.delete_state(message.from_user.id)
        start_murkup = get_start_markup()
        bot.send_message(
            message.from_user.id,
            f"Выберите следующее действие",
            reply_markup=start_murkup,
        )
    except IndexError:
        bot.send_message(
            message.from_user.id, "К сожалению не получилось найти такой фильм😢"
        )
        bot.delete_state(message.from_user.id)
    except Exception:
        bot.send_message(
            message.from_user.id, "К сожалению произошла какая то ошибка😢"
        )
        bot.delete_state(message.from_user.id)


@bot.message_handler(state="*", commands=["search by type"])
def type_film(message: Message) -> None:
    """
    Функция обрабатывающая команду search by type, запрашивает количество фильмов и обращается к базе данных чтобы в
    дальнейшем записать в нее информацию о фильме
    :param message:
    :return:
    """
    bot.send_message(message.from_user.id, "Введите количество желаемых фильмов")
    user_id = message.from_user.id
    bot.set_state(message.from_user.id, UserState.new_film_search_by_type)
    with bot.retrieve_data(message.from_user.id) as data:
        data["new_film"] = {"user_id": user_id}


@bot.message_handler(state=UserState.new_film_search_by_type)
def count_type_films(message: Message) -> None:
    """
    Функция проверяющая корректность ввода количества фильмов, запрашивающая тип фильмов, начинающая цикл по запросам
    и записям фильмов в базу данных
    :param message:
    :return:
    """
    global global_count
    count = message.text
    if not count.isdigit():
        bot.send_message(
            message.from_user.id,
            "Количество фильмов должно быть числом, попробуйте ещё раз",
        )
        bot.register_next_step_handler(message, count_type_films)
        return
    types_murkup = get_types_markup()
    bot.send_message(
        message.from_user.id, "Выберите тип фильма", reply_markup=types_murkup
    )
    global_count = int(count)
    bot.register_next_step_handler(message, search_type_films)


def search_type_films(message: Message) -> None:
    """
    Функция создающая запрос API серверу для получения информации о фильме по типу и записывающая информацию в базу
    данных
    :param message:
    :return:
    """
    global global_count
    global type_films
    try:
        if message.text == "Фильм":
            type_films = "movie"
        if message.text == "Сериал":
            type_films = "tv-series"
        if message.text == "Мультфильм":
            type_films = "cartoon"
        if message.text == "Аниме":
            type_films = "anime"
        if type_films != "":
            url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&type={type_films}"
            headers = {"accept": "application/json", "X-API-KEY": X_API_KEY}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                bot.send_message(
                    message.from_user.id, "К сожалению произошла какая то ошибка😢"
                )
            try:
                for i in range(global_count):
                    data = json.loads(response.text)
                    new_data = data_reader(message, data, i)
                    if new_data is False:
                        continue
                    new_film = history_films(**new_data["new_film"])
                    new_film.save()
                    bot.send_message(
                        message.from_user.id,
                        f"Название: {new_data["new_film"]["title"]}"
                        f"\nОписание: {new_data["new_film"]["description"]}"
                        f"\nРейтинг: {new_data["new_film"]["rating"]}"
                        f"\nГод выпуска: {new_data["new_film"]["year"]}"
                        f"\nЖанр: {new_data["new_film"]["genre"]}"
                        f"\nВозрастной рейтинг: {new_data["new_film"]["age_rating"]}"
                        f"\n{new_data["new_film"]["poster"]}",
                        )
            except IndexError:
                bot.send_message(
                    message.from_user.id, f"К сожалению фильмы такого типа закончились😢")
            except Exception:
                bot.send_message(
                    message.from_user.id, f"К сожалению произошла какая то ошибка😢"
                )
        else:
            bot.send_message(
                message.from_user.id,
                f"К сожалению нет такого варианта ответа, выберите количество "
                f"фильмов заново и тип фильма из предложенных вариантов",
            )
            bot.register_next_step_handler(message, count_type_films)
    finally:
        bot.delete_state(message.from_user.id)
        start_murkup = get_start_markup()
        global_count = 0
        type_films = ""
        bot.send_message(
            message.from_user.id,
            f"Выберите следующее действие",
            reply_markup=start_murkup,
            )



@bot.message_handler(state="*", commands=["search by genre"])
def genre_film(message: Message) -> None:
    """
    Функция обрабатывающая команду search by genre, запрашивает количество фильмов и обращается к базе данных чтобы в
    дальнейшем записать в нее информацию о фильме
    :param message:
    :return:
    """
    bot.send_message(message.from_user.id, "Введите количество желаемых фильмов")
    user_id = message.from_user.id
    bot.set_state(message.from_user.id, UserState.new_film_genres)
    with bot.retrieve_data(message.from_user.id) as data:
        data["new_film"] = {"user_id": user_id}


@bot.message_handler(state=UserState.new_film_genres)
def count_genre_films(message: Message) -> None:
    """
    Функция проверяющая корректность ввода количества фильмов, запрашивающая жанр фильмов, начинающая цикл по запросам
    и записям фильмов в базу данных
    :param message:
    :return:
    """
    count = message.text
    if not count.isdigit():
        bot.send_message(
            message.from_user.id,
            "Количество фильмов должно быть числом, попробуйте ещё раз",
        )
        bot.register_next_step_handler(message, count_genre_films)
        return
    genre_murkup = get_genre_markup()
    bot.send_message(message.from_user.id, "Выберите жанр фильма", reply_markup=genre_murkup)
    bot.register_next_step_handler(message, search_genre_films, int(count))


def search_genre_films(message: Message, count: int) -> None:
    """
    Функция создающая запрос API серверу для получения информации о фильме по жанру и записывающая информацию в базу
    данных
    :param message:
    :param i:
    :param count:
    :return:
    """
    global genre_films
    if message.text == "Комедия":
        genre_films = "комедия"
    if message.text == "Драма":
        genre_films = "драма"
    if message.text == "Ужасы":
        genre_films = "ужасы"
    if message.text == "Боевик":
        genre_films = "боевик"
    if genre_films != "":
        url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&genres.name={genre_films}"
        headers = {"accept": "application/json", "X-API-KEY": X_API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            bot.send_message(
                message.from_user.id, "К сожалению произошла какая то ошибка😢"
            )
        try:
            data = json.loads(response.text)
            for i in range(count):
                new_data = data_reader(message, data, i)
                if new_data is False:
                    continue
                new_film = history_films(**new_data["new_film"])
                new_film.save()
                bot.send_message(
                    message.from_user.id,
                    f"Название: {new_data["new_film"]["title"]}"
                    f"\nОписание: {new_data["new_film"]["description"]}"
                    f"\nРейтинг: {new_data["new_film"]["rating"]}"
                    f"\nГод выпуска: {new_data["new_film"]["year"]}"
                    f"\nЖанр: {new_data["new_film"]["genre"]}"
                    f"\nВозрастной рейтинг: {new_data["new_film"]["age_rating"]}"
                    f"\n{new_data["new_film"]["poster"]}",
                )
        except IndexError:
            bot.send_message(
                message.from_user.id, f"К сожалению фильмы такого жанра закончились😢")
            return
        except Exception:
            bot.send_message(
                message.from_user.id, f"К сожалению произошла какая то ошибка😢"
            )
        finally:
            start_murkup = get_start_markup()
            bot.delete_state(message.from_user.id)
            genre_films = ""
            bot.send_message(
                message.from_user.id,
                f"Выберите следующее действие",
                reply_markup=start_murkup,
            )
    else:
        bot.send_message(
            message.from_user.id,
            f"К сожалению нет такого варианта ответа, выберите количество "
            f"фильмов заново и тип фильма из предложенных вариантов",
        )
        bot.register_next_step_handler(message, count_type_films)


@bot.message_handler(state="*", commands=["movie_by_rating"])
def choice_rating(message: Message) -> None:
    """
    Функция обрабатывающая команду movie_by_rating, запрашивает количество выводимых фильмов и обращается к базе данных
    чтобы в дальнейшем записать в нее информацию о фильме
    :param message:
    :return:
    """
    bot.send_message(message.from_user.id, "Введите количество желаемых фильмов")
    user_id = message.from_user.id
    bot.set_state(message.from_user.id, UserState.new_film_rating)
    with bot.retrieve_data(message.from_user.id) as data:
        data["new_film"] = {"user_id": user_id}


@bot.message_handler(state=UserState.new_film_rating)
def count_films(message: Message) -> None:
    """
    Функция проверяющая корректность ввода количества фильмов, запрашивающая рейтинг фильма, начинающая цикл по запросам
    и записям фильмов в базу данных
    :param message:
    :return:
    """
    count = message.text
    if not count.isdigit():
        bot.send_message(
            message.from_user.id,
            "Количество фильмов должно быть числом, попробуйте ещё раз",
        )
        bot.register_next_step_handler(message, count_films)
        return
    bot.send_message(message.from_user.id, "Введите рейтинг Фильма/Сериала")
    bot.register_next_step_handler(message, search_rating, int(count))


def search_rating(message: Message, count: int) -> None:
    """
    Функция создающая запрос API серверу для получения информации о фильме по рейтингу и записывающая информацию в базу
    данных
    :param message:
    :param i:2
    :param count:
    :return:
    """
    try:
        rating = message.text.strip()
        pattern1 = re.compile(r"^\d+(\.\d+)?-\d+(\.\d+)?$")
        result_rating = rating
        if not pattern1.match(rating) is None:
            if rating.split("-") is list:
                nums = rating.split("-")
                if float(nums[0]) > float(nums[1]):
                    result_rating = nums[1] + "-" + nums[0]
                else:
                    result_rating = nums[0] + "-" + nums[1]
        else:
            result_rating = rating
            pattern2 = re.compile(r"^\d[.]\d+$")
            if not pattern2.match(result_rating) is None:
                rat = rating.split(".")
                check = rat[0] + rat[1]
                if not check.isdigit():
                    raise TypeError
            else:
                if not result_rating.isdigit():
                    raise TypeError
                if not 0 <= float(result_rating) <= 10:
                    raise ValueError
        url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&rating.kp={result_rating}"
        headers = {"accept": "application/json", "X-API-KEY": X_API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            bot.send_message(
                message.from_user.id, "К сожалению произошла какая то ошибка😢"
            )
        try:
            data = json.loads(response.text)
            for i in range(count):
                new_data = data_reader(message, data, i)
                new_film = history_films(**new_data["new_film"])
                new_film.save()
                bot.send_message(
                    message.from_user.id,
                    f"Название: {new_data["new_film"]["title"]}"
                    f"\nОписание: {new_data["new_film"]["description"]}"
                    f"\nРейтинг: {new_data["new_film"]["rating"]}"
                    f"\nГод выпуска: {new_data["new_film"]["year"]}"
                    f"\nЖанр: {new_data["new_film"]["genre"]}"
                    f"\nВозрастной рейтинг: {new_data["new_film"]["age_rating"]}"
                    f"\n{new_data["new_film"]["poster"]}",
                )
        except IndexError:
            time.sleep(0.3)
            if i == 0:
                bot.send_message(
                    message.from_user.id,
                    "К сожалению фильмов с таким рейтингом не существует",
                )
            else:
                bot.send_message(
                    message.from_user.id,
                    "К сожалению фильмы с таким рейтингом закончились",
                )
            return
        except Exception as e:
            print(e)
            bot.send_message(
                message.from_user.id, f"К сожалению произошла какая то ошибка😢"
            )
            return
        finally:
            start_murkup = get_start_markup()
            bot.delete_state(message.from_user.id)
            bot.send_message(
                message.from_user.id,
                f"Выберите следующее действие",
                reply_markup=start_murkup,
            )
    except TypeError:
        bot.send_message(
            message.from_user.id,
            "Рейтинг должен быть числом, введите количество фильмов пожалуйста заново.",
        )
        time.sleep(0.2)
        bot.register_next_step_handler(message, count_films)
    except ValueError:
        bot.send_message(
            message.from_user.id,
            "Рейтинг должен быть больше 0 и меньше 10, ведите количество фильмов "
            "пожалуйста заново.",
        )
        time.sleep(0.2)
        bot.register_next_step_handler(message, count_films)


@bot.message_handler(commands=["history"])
def history(message: Message) -> None:
    """
    Функция обращающаяся к базе данных и выводящая всю информацию из нее
    :param message:
    :return:
    """
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        murkup = types.InlineKeyboardMarkup()
        but = types.InlineKeyboardButton("Старт", callback_data="start")
        murkup.add(but)
        bot.send_message(
            message.from_user.id,
            "Извините, но вы ещё не зарегистрировались, для этого нажмите на кнопку \n\n"
            "*/start*",
            parse_mode="Markdown",
        )
        return
    result = []
    result.extend(map(str, user.films))
    start_murkup = get_start_markup()
    if len(result) == 0:
        bot.send_message(message.from_user.id, "Извините, но ваша история еще пуста.")
        bot.send_message(
            message.from_user.id,
            f"Выберите следующее действие",
            reply_markup=start_murkup,
        )
    else:
        for film in result:
            bot.send_message(message.from_user.id, film)
        bot.send_message(
            message.from_user.id,
            f"Выберите следующее действие",
            reply_markup=start_murkup,
        )


@bot.message_handler(content_types=["text"])
def func_with_resend_message(message):
    """
    Функция обрабатывающая работу Reply кнопок
    :param message:
    :return:
    """
    print(message.text)
    if message.text == "Поиск фильма/сериала по названию":
        print('choice_name')
        choice_name(message)
    if message.text == "Поиск фильмов/сериалов по рейтингу":
        print('choice_rating')
        choice_rating(message)
    if message.text == "История запросов":
        print('history')
        history(message)
    if message.text == "Поиск фильмов/сериалов по типу":
        print('type_film')
        type_film(message)
    if message.text == "Поиск фильмов/сериалов по жанру":
        print('genre_film')
        genre_film(message)


if __name__ == "__main__":
    create_models()
    bot.add_custom_filter(StateFilter(bot))
    bot.set_my_commands([BotCommand(*cmd) for cmd in DEFAULT_COMMANDS])
    bot.polling()
