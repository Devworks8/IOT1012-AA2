from flask import Flask
from flask_restx import Api, Resource, fields
import GoogleBooksAPI.GBFunctions
import PubVar

app = Flask(__name__)
api = Api(app,
          version=PubVar.VERSION,
          title=PubVar.TITLE,
          description=PubVar.DESCRIPTION,
          doc=PubVar.DOC)

ns = api.namespace(PubVar.NS, description=PubVar.NSDESCRIPTION)

book_model = api.model('books', {
    'id': fields.Integer(readonly=True, description='The book unique identifier'),
    'title': fields.String(required=False, description='Book title'),
    'author': fields.String(required=False, description='Book author'),
    'isbn': fields.String(required=False, description='Book ISBN'),
    'publisher': fields.String(required=False, description='Book publisher'),
    'genre': fields.String(required=False, description='Book category'),
    'type': fields.String(required=False, description='Book type')
})


class CRUDUtil(object):
    def __init__(self):
        self.counter = 0
        self.books = []

    def get(self, id):
        for book in self.books:
            if book['id'] == id:
                return book
        api.abort(404, f"book {id} doesn't exist.")

    def create(self, data):
        book = data
        book["id"] = self.counter = self.counter + 1

        if "isbn" in book.keys():
            resp = GoogleBooksAPI.GBFunctions.fetch_query("isbn", book.get("isbn"))
            book["title"] = resp["title"]
            book["author"] = resp["authors"][0]
            book["isbn"] = data.get("isbn")
            book["publisher"] = resp["publisher"]
            if "categories" in resp.keys():
                book["genre"] = resp["categories"][0]
            else:
                book["genre"] = "Unknown"
            book["type"] = resp["printType"]

        elif "title" in book.keys():
            resp = GoogleBooksAPI.GBFunctions.fetch_query("title", book.get("title"))
            book["title"] = book.get("title")
            book["author"] = resp["authors"][0]
            book["isbn"] = resp["industryIdentifiers"][0]["identifier"]
            book["publisher"] = resp["publisher"]
            if "categories" in resp.keys():
                book["genre"] = resp["categories"][0]
            else:
                book["genre"] = "Unknown"
            book["type"] = resp["printType"]

        self.books.append(book)
        return book

    def update(self, id, data):
        book = self.get(id)
        book.update(data)  # this is the dict_object update method

        return book

    def delete(self, id):
        book = self.get(id)
        self.books.remove(book)


@ns.route('/')  # keep in mind this our ns-namespace (books/)
class BookList(Resource):
    """Shows a list of all books, and lets you POST to add new pins"""

    @ns.marshal_list_with(book_model)
    def get(self):
        """List all pins"""
        return crud_util.books

    @ns.expect(book_model)
    @ns.marshal_with(book_model, code=201)
    def post(self):
        """Create a new book"""
        return crud_util.create(api.payload)


@ns.route('/<int:id>')
@ns.response(404, 'book not found')
@ns.param('id', 'The book identifier')
class Book(Resource):
    """Show a single book item and lets you update/delete them"""

    @ns.marshal_with(book_model)
    def get(self, id):
        """Fetch a book given its resource identifier"""
        return crud_util.get(id)

    @ns.response(204, 'pin deleted')
    def delete(self, id):
        """Delete a book given its identifier"""
        crud_util.delete(id)
        return '', 204

    @ns.expect(book_model, validate=True)
    @ns.marshal_with(book_model)
    def put(self, id):
        """Update a book given its identifier"""
        return crud_util.update(id, api.payload)

    @ns.expect(book_model)
    @ns.marshal_with(book_model)
    def patch(self, id):
        """Partially update a book given its identifier"""
        return crud_util.update(id, api.payload)


crud_util = CRUDUtil()
# pin_util.create({'pin_num': 23, 'color': 'red', 'state': 'off'})

# from flask import *
# import json
# import GoogleBooksAPI.GBFunctions
#
#
# app = Flask(__name__)
#
# counter = 0
# data_set = {'id': 0,
#             'Title': 'Unknown',
#             'Author': 'Unknown',
#             'ISBN': 'Unknown',
#             'Publisher': 'Unknown',
#             'Genre': 'Unknown',
#             'Type': 'Unknown'}
#
# context = []
#
#
# @app.route('/', methods=['GET'])
# def root():
#     return json.dumps(data_set)
#
#
# @app.route('/all/', methods=['GET'])
# def get_all():
#     return json.dumps(context)
#
#
# @app.route('/<int:id>', methods=['GET'])
# def request(id):
#     id_query = str(request.args.get('id'))  # /id/?id=
#     for book in context:
#         if book['id'] == id_query:
#             return json.dumps(book)
#
#
# @app.route('/create/<query>', methods=['POST'])
# def create(query):
#     global counter
#     results = {}
#     if query == 'isbn':
#         data = request.form['isbn']
#         resp = GoogleBooksAPI.GBFunctions.fetch_query('isbn', request.args.get('isbn'))
#         results['id'] = counter = counter = 1
#         results['Title'] = resp["title"]
#         results['Author'] = resp["authors"][0]
#         results['ISBN'] = data
#         results['Genre'] = resp["Categories"]
#         results['Type'] = resp["PrintType"]
#
#         context.append(results)
#
#     elif query == 'title':
#         data = request.form['title']
#         resp = GoogleBooksAPI.GBFunctions.fetch_query('title', request.args.get('title'))
#         results['id'] = counter = counter = 1
#         results['Title'] = data
#         results['Author'] = resp["authors"][0]
#         results['ISBN'] = resp["IndustryIdentifiers"][0].Identifier
#         results['Genre'] = resp["Categories"]
#         results['Type'] = resp["PrintType"]
#         context.append(results)
#     else:
#         results = {'Message': 'Invalid arguments provided.'}
#
#     return json.dumps(results)
#
#
# @app.route('/modify/<int:id>', methods=['PATCH'])
# def modify(id):
#     found_book = None
#     for book in context:
#         if book['id'] == id:
#             found_book = book
#             break
#
#     if found_book is None:
#         return json.dumps({'Message': 'Book not found.'})
#     else:
#         found_book.update(request.args)
#         return found_book
#
#
# @app.route('/delete/<int:id>', methods=['DELETE'])
# def delete(id):
#     for book in context:
#         if book['id'] == id:
#             context.remove(book)
#             break
