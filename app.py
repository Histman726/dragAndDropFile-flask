from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'cloud files'
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
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/archivos')
def archivos_uploaded():
    return render_template('archivos subidos.html')


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'POST':
        user = User.query.filter_by(name=request.form['txtNombre'], password=request.form['txtPassword']).first()
        session['nombre'] = user.name

    return render_template('perfil.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        user = User(name=request.form['txtNombre'], password=request.form['txtPassword'])
        db.session.add(user)
        db.session.commit()
        session['nombre'] = user.name
        session['id'] = user.id
        return redirect(url_for('home'))
    return render_template('registro.html')


@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect(url_for('perfil'))


if __name__ == '__main__':
    app.run(debug=True)
    with app.app_context():
        db.create_all()
