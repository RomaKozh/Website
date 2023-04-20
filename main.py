from flask import Flask, redirect, render_template, request, make_response, session, jsonify
from data import db_session
from data.users import User
from data.news import News
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.news import NewsForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = '123zxcqweasd'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    return render_template('index.html', title='Главная', news=news)


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
        user = User(
            name=form.name.data,
            email=form.email.data,
            avatar=form.avatar.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return render_template('register.html', title='Регистрация',
                               form=form, message='Пользователь успешно создан')
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
    return render_template('profile.html', title='Профиль')


@app.route('/news')
def news():
    return render_template('news.html')


def main():
    db_session.global_init('db/website.db')
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()