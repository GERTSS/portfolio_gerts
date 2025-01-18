from flask import Flask, request

# from flask_restful import Api, Resource
from flask_restx import Api, Resource
from marshmallow import ValidationError

from models import (
    DATA_BOOKS,
    DATA_AUTHORS,
    get_all_books,
    init_db,
    add_book,
    get_book,
    delete_book,
    update_book_by_id,
    add_author,
    delete_books_by_id_author,
    get_all_books_by_author,
)
from schemas import BookSchema, AuthorSchema

app = Flask(__name__)
api = Api(app, prefix="/api")


@api.route("/books")
class BookList(Resource):
    def get(self) -> tuple[list[dict], int]:
        schema = BookSchema()
        return schema.dump(get_all_books(), many=True), 200

    def post(self) -> tuple[dict, int]:
        data = request.json
        schema = BookSchema()
        try:
            book = schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400

        book = add_book(book)
        return schema.dump(book), 201


@api.route("/books/<int:book_id>")
class BookInfo(Resource):
    def get(self, book_id) -> tuple[list[dict], int]:
        schema = BookSchema()
        return schema.dump(get_book(book_id)), 200

    def delete(self, book_id) -> tuple[dict, int]:
        schema = BookSchema()
        return schema.dump(delete_book(book_id)), 200

    def patch(self) -> tuple[dict, int]:
        data = request.json
        schema = BookSchema()
        try:
            book = schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400
        book = update_book_by_id(book)
        return schema.dump(book), 201


@api.route("/authors/<int:author_id>")
class AuthorInfo(Resource):
    def get(self, author_id) -> tuple[list[dict], int]:
        schema = BookSchema()
        return schema.dump(get_all_books_by_author(author_id), many=True), 200

    def delete(self, author_id) -> tuple[dict, int]:
        schema = AuthorSchema()
        return schema.dump(delete_books_by_id_author(author_id)), 200


@api.route("/authors/")
class AddAuthor(Resource):
    def post(self) -> tuple[dict, int]:
        data = request.json
        schema = AuthorSchema()
        try:
            author = schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400
        author = add_author(author)
        return schema.dump(author), 201


if __name__ == "__main__":
    init_db(initial_records=DATA_BOOKS, initial_records_authors=DATA_AUTHORS)
    app.run(debug=True)
