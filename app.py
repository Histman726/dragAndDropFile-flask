from flask import Flask, render_template, redirect, url_for, request, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'cloud files'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///files.sqlite"
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'pptx'}
FILES_UPLOADS_FOLDER = 'C:\\Users\\monic\\PycharmProjects\\dragandDropFileFlask\\static\\uploads\\'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    files = db.relationship('Files', backref='owner')


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    fecha = db.Column(db.String(50))


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        now = datetime.now()

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_file = Files(filename=file.filename, owner_id=session['id'], fecha=now.strftime("%m/%d/%Y, %H:%M:%S"))
            db.session.add(new_file)
            db.session.commit()
            print('File successfully uploaded ' + file.filename + ' to the database!')
        else:
            print('Invalid Uplaod only txt, pdf, png, jpg, jpeg, gif')
        msg = 'Success Uplaod'
    return jsonify(msg)


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/archivos')
def archivos_uploaded():
    try:
        files = db.session.query(Files).filter(Files.owner_id == session['id'])
        print(len(files))
    except:
        files = []

    if len(files)==0:
        files = 0
    return render_template('archivos subidos.html', files=files)


@app.route('/archivos/download/<int:id>')
def download(id):
    file = Files.query.filter_by(id=id).first()
    return send_from_directory(FILES_UPLOADS_FOLDER, file.filename, as_attachment=True)


@app.route('/archivos/rename/<int:id>')
def rename_view(id):
    return render_template('rename.html', id=id)


@app.route('/rename', methods=['POST', 'GET'])
def rename():
    id = request.form['txtId']
    new_filename = request.form['txtNuevoNombre']
    file = Files.query.filter_by(id=id).first()
    filename, ext = os.path.splitext(file.filename)
    os.rename(FILES_UPLOADS_FOLDER + file.filename, FILES_UPLOADS_FOLDER + new_filename + ext)
    file.filename = new_filename + ext
    db.session.commit()
    return redirect(url_for('archivos_uploaded'))


@app.route('/archivos/delete/<int:id>')
def delete(id):
    file = Files.query.filter_by(id=id).first()
    os.unlink(FILES_UPLOADS_FOLDER + file.filename)
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for('archivos_uploaded'))


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'POST':
        user = User.query.filter_by(name=request.form['txtNombre'], password=request.form['txtPassword']).first()
        session['nombre'] = user.name
        session['id'] = user.id

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
