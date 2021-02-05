from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, request
from flask import jsonify
from marshmallow_sqlalchemy import ModelSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
api = Api(app)

class Notes(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    content = db.Column(db.String(250), nullable=False)
    creation_date = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def __init__(self, name, content):
        self.name = name
        self.content = content

class NotesSchema(ModelSchema):
    class Meta:
        model = Notes


note_schema = NotesSchema()
notes_schema = NotesSchema(many=True)

class PostListResource(Resource):
    def get(self):
        notes = Notes.query.all()   
        return notes_schema.dump(notes)

    def post(self):
        name = request.json['name']
        content = request.json['content']
        note = Notes(name, content)
        db.session.add(note)
        db.session.commit()
        return note_schema.dump(note)


class PostResource(Resource):
    def get(self, note_id):
        note = Notes.query.get_or_404(note_id)
        return note_schema.dump(note)

    def put(self, note_id):
        note = Notes.query.get_or_404(note_id)

        if 'name' in request.json:
            note.name = request.json['name']
        if 'content' in request.json:
            note.content = request.json['content']

        db.session.commit()
        return note_schema.dump(note)

    def delete(self, note_id):
        note = Notes.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return '', 204


api.add_resource(PostListResource, '/notes')
api.add_resource(PostResource, '/notes/<int:note_id>')


if __name__ == '__main__':
    app.run(port ="8001" ,debug=True)
