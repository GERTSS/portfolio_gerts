from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateField,
    ForeignKeyField,
    IntegerField,
    Model,
    DecimalField,
    SqliteDatabase,
)

from config import DB_PATH

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()


class history_films(BaseModel):
    title = CharField()
    description = CharField()
    year = CharField()
    rating = CharField()
    genre = CharField()
    age_rating = CharField()
    poster = CharField()
    user = ForeignKeyField(User, backref="films")
    due_data = CharField()

    def __str__(self):
        return (("Название Фильма\Сериала - {title}\nОписание Фильма\Сериала - {description}"
                "\nГод выпуска - {year}\nОбщий рейтинг - {rating}"
                "\nЖанр - {genre}\nВозрастной рейтинг - {age_rating}"
                "\nДата и время запроса - {due_data}\n{poster}").format(
            title=self.title,
            age_rating=self.age_rating,
            description=self.description,
            year=self.year,
            rating=self.rating,
            genre=self.genre,
            poster=self.poster,
            due_data=self.due_data
        ))


def create_models():
    db.create_tables(BaseModel.__subclasses__())