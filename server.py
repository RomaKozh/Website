from flask import Flask, redirect, render_template, make_response, jsonify, url_for, request
import sqlite3
import os
from data import db_session
from data.users import User
from data.news import News
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.edit_profile import EditForm
from forms.news import NewsForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = '123zxcqweasd'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    read_blob_data(user_id)
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).order_by(News.id.desc())
    read_blob_data_news()
    return render_template('index.html', title='Главная', news=news,
                           avatar=url_for('static', filename='images/avatar.jpg'))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message='Эта почта уже используется')
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message='Это имя уже используется')
        ava = form.avatar.data.read()
        if not ava:
            standart_ava = open('static/images/standart.jpg', 'rb')
            binary = sqlite3.Binary(standart_ava.read())
        else:
            binary = sqlite3.Binary(ava)
        user = User(
            name=form.name.data,
            email=form.email.data,
            avatar=binary
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return render_template('register.html', title='Регистрация',
                               form=form, message='Пользователь успешно создан',
                               avatar=url_for('static', filename='images/avatar.jpg'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Профиль',
                           avatar=url_for('static', filename='images/avatar.jpg'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        ava = form.avatar.data.read()
        if not ava:
            standart_ava = open('static/images/standart.jpg', 'rb')
            binary = sqlite3.Binary(standart_ava.read())
        else:
            binary = sqlite3.Binary(ava)
        user.set_name(form.name.data)
        user.set_email(form.email.data)
        user.set_avatar(binary)
        db_sess.commit()
        return render_template('edit.html', title='Редактирование профиля', form=form,
                               message='Профиль успешно изменен',
                               avatar=url_for('static', filename='images/avatar.jpg'))
    return render_template('edit.html', title='Редактирование профиля', form=form,
                           avatar=url_for('static', filename='images/avatar.jpg'))


@app.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        binary = sqlite3.Binary(form.photo.data.read())
        news = News(title=form.title.data,
                    description=form.description.data,
                    content=form.content.data,
                    photo=binary)
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return render_template('add_news.html', message="Новость успешно создана", form=form,
                               avatar=url_for('static', filename='images/avatar.jpg'))
    return render_template('add_news.html', form=form,
                           avatar=url_for('static', filename='images/avatar.jpg'))


@app.route('/edit_news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if form.validate_on_submit():
        if news.user.id == current_user.id or current_user.admin is True:
            binary = sqlite3.Binary(form.photo.data.read())
            news.set_title(form.title.data)
            news.set_description(form.description.data)
            news.set_content(form.content.data)
            news.set_photo(binary)
            db_sess.commit()
            return render_template('edit_news.html', form=form, title=news.title, photo=news.photo,
                                   description=news.description, content=news.content,
                                   message='Новость успешно изменена',
                                   avatar=url_for('static', filename='images/avatar.jpg'))
        return render_template('edit_news.html', form=form, title=news.title, photo=news.photo,
                               description=news.description, content=news.content,
                               message='Недостаточно прав',
                               avatar=url_for('static', filename='images/avatar.jpg'))
    return render_template('edit_news.html', form=form, title=news.title, photo=news.photo,
                           description=news.description, content=news.content,
                           avatar=url_for('static', filename='images/avatar.jpg'))


@app.route('/news/<title>/<int:id>')
def news(title, id):
    db_sess = db_session.create_session()
    news_data = db_sess.query(News).filter(News.id == id).first()
    if news_data.user:
        return render_template('news.html', title=title, id=id, content=news_data.content,
                               photo=news_data.photo,
                               created_date=news_data.created_date, author=news_data.user,
                               avatar=url_for('static', filename='images/avatar.jpg'))
    return render_template('news.html', title=title, content=news_data.content,
                           photo=news_data.photo, created_date=news_data.created_date,
                           avatar=url_for('static', filename='images/avatar.jpg'))


@app.route('/delete_news/<int:id>')
@login_required
def delete_news(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if news.user.id == current_user.id or current_user.admin is True:
        db_sess.delete(news)
        db_sess.commit()
    return redirect('/')


def write_to_file(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)


def read_blob_data(id):
    sqlite_con = sqlite3.connect('db/website.db')
    cur = sqlite_con.cursor()
    sql_fetch_blob_query = """SELECT avatar from users where id = ?"""
    cur.execute(sql_fetch_blob_query, (id, ))
    record = cur.fetchall()
    path = os.path.join('static/images', 'avatar.jpg')
    if record:
        write_to_file(record[0][0], path)
    cur.close()
    sqlite_con.close()


def read_blob_data_news():
    sqlite_con = sqlite3.connect('db/website.db')
    cur = sqlite_con.cursor()
    sql_fetch_blob_query = """SELECT * from news"""
    cur.execute(sql_fetch_blob_query)
    record = cur.fetchall()
    if record:
        for row in record:
            id = row[0]
            photo = row[4]
            path = os.path.join('static/images', str(id) + '.jpg')
            write_to_file(photo, path)
    cur.close()
    sqlite_con.close()


def main():
    db_session.global_init('db/website.db')
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')


if __name__ == '__main__':
    main()
