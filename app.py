from flask import Flask, request, redirect, url_for
from flask_restful import Api, Resource
from models import db, Book

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
api = Api(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for("books"))


class BookListResource(Resource):
    def get(self):
        author_filter = request.args.get("author")
        if author_filter:
            books = Book.query.filter_by(author=author_filter).all()
        else:
            books = Book.query.all()

        return [book.to_dict() for book in books], 200

    def post(self):
        data = request.get_json()

        if not data:
            return {"error": "Missing JSON body"}, 400

        title = data.get("title")
        author = data.get("author")
        year = data.get("year")

        if not title or not author or not year:
            return {"error": "Title, Author, and Year are required"}, 400

        try:
            year = int(year)
        except ValueError:
            return {"error": "Year must be an integer"}, 400

        new_book = Book(title=title, author=author, year=year)
        db.session.add(new_book)
        db.session.commit()

        return new_book.to_dict(), 201


class BookResource(Resource):
    def get(self, id):
        book = Book.query.get_or_404(id)
        return book.to_dict(), 200

    def put(self, id):
        book = Book.query.get_or_404(id)
        data = request.get_json()

        if "title" in data:
            book.title = data["title"]
        if "author" in data:
            book.author = data["author"]
        if "year" in data:
            try:
                book.year = int(data["year"])
            except ValueError:
                return {"error": "Year must be an integer"}, 400

        db.session.commit()
        return book.to_dict(), 200

    def delete(self, id):
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted"}, 200

api.add_resource(BookListResource, "/books", endpoint="books")
api.add_resource(BookResource, "/books/<int:id>", endpoint="book")

if __name__ == "__main__":
    app.run(debug=True)
