from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///files.sqlite"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    files = db.relationship('Files', backref='owner')


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


@app.route('/')
def main():
    user = User(name='ivan', password='123')
    db.session.add(user)
    db.session.commit()
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
    with app.app_context():
        db.create_all()
