import datetime
from os import abort

from flask import Flask, render_template, request
from data import db_session, users_api, themes_api
from data.users import User
from data.themes import Themes
from data.invites import Invites
from data.messages import Messages
from forms.create_invite import Create_inviteForm
from forms.login import LoginForm
from forms.theme_add import Theme_addForm
from forms.message_add import Message_addForm
from forms.user import RegisterForm
from werkzeug.utils import redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

def main():
    db_session.global_init ( "db/blogs.db" )
    db_sess = db_session.create_session()
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(themes_api.blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)

    @app.route ( "/" )
    def index():
        db_sess = db_session.create_session ()
        themes = db_sess.query(Themes).filter()
        return render_template ( "index.html", themes=themes )

    @app.route ( '/register', methods=['GET', 'POST'] )
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit ():
            if form.password.data != form.password_again.data:
                return render_template ( 'register.html', title='Регистрация',
                                         form=form,
                                         message="Пароли не совпадают" )
            db_sess = db_session.create_session ()
            if db_sess.query ( User ).filter ( User.name == form.name.data ).first ():
                return render_template ( 'register.html', title='Регистрация',
                                         form=form,
                                         message="Такой пользователь уже есть" )
            invite = db_sess.query ( Invites ).filter ( Invites.invite == form.invite.data ).first()
            if invite:
                if invite.active == 0:
                    print(form.invite.data)
                    return render_template ( 'register.html', title='Регистрация',
                                             form=form,
                                             message="Введён нерабочий код приглашения" )

                else:
                    user = User(name=form.name.data, inviter=invite.creator)
                    user.set_password ( form.password.data )
                    user.available_invites = 2
                    db_sess.add ( user )
                    invite.active = 0
                    invite.invited_user = form.name.data
                    db_sess.commit ()
                    return redirect ( '/login' )
        return render_template ( 'register.html', title='Регистрация', form=form )

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.name == form.name.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")



    @app.route('/create_invite', methods=['GET', 'POST'])
    @login_required
    def create_invite():
        form = Create_inviteForm()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == current_user.name).first()
        available_invites = str(user.available_invites)
        if form.validate_on_submit():
            db_sess_submit = db_session.create_session()
            invites = Invites()
            invites.invite = form.invite.data
            invites.creator = current_user.name
            invites.active = 1
            current_user.invites.append(invites)
            if current_user.available_invites > 0:
                current_user.available_invites -= 1
            db_sess_submit.merge(current_user)
            db_sess_submit.commit()
            return redirect('/')
        return render_template('create_invite.html', title='Создание приглашения', available_invites=available_invites,
                               form=form)

    @app.route ("/theme/<int:id>", methods=['GET', 'POST'])
    @login_required
    def show_theme(id):
        form = Message_addForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            messages = Messages()
            messages.content = form.content.data
            messages.theme_id = id
            current_user.messages.append(messages)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/theme/'+str(id))
        db_sess = db_session.create_session ()
        theme_message = db_sess.query(Themes).filter((Themes.id == id))
        messages = db_sess.query(Messages).filter((Messages.theme_id == id))
        return render_template ( "theme.html", theme_message=theme_message, messages=messages, form=form)

    @app.route ("/theme/<int:themeId>/message/<int:messageId>/edit_message", methods=['GET', 'POST'])
    @login_required
    def edit_message(themeId, messageId):
        form = Message_addForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            message = db_sess.query ( Messages ).filter (Messages.theme_id == themeId, Messages.id == messageId).first ()

            if message:
                form.content.data = message.content
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            message = db_sess.query ( Messages ).filter ( Messages.theme_id == themeId,
                                                          Messages.id == messageId ).first ()
            if message:
                message.content = form.content.data
                db_sess.commit()
                return redirect('/theme/'+str(themeId))
            else:
                abort(404)
        return render_template('theme.html',
                               title='Редактирование комментария',
                               form=form
                               )

    @app.route("/theme/<int:themeId>/message/<int:messageId>/delete_message", methods=['GET', 'POST'])
    @login_required
    def delete_message(themeId, messageId):
        db_sess = db_session.create_session()
        message = db_sess.query ( Messages ).filter ( Messages.theme_id == themeId,
                                                      Messages.id == messageId ).first ()

        if message:
            db_sess.delete(message)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/theme/'+str(themeId))

    @app.route('/theme_add', methods=['GET', 'POST'])
    @login_required
    def add_themes():
        form = Theme_addForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            themes = Themes()
            themes.title = form.title.data
            themes.content = form.content.data
            current_user.themes.append(themes)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('theme_add.html', title='Добавление темы',
                               form=form)

    @app.route('/theme_edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_themes(id):
        form = Theme_addForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            themes = db_sess.query(Themes).filter(Themes.id == id,
                                              Themes.user == current_user
                                              ).first()
            if themes:
                form.title.data = themes.title
                form.content.data = themes.content
                #form.is_private.data = themes.is_private
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            themes = db_sess.query(Themes).filter(Themes.id == id,
                                              Themes.user == current_user
                                              ).first()
            if themes:
                themes.title = form.title.data
                themes.content = form.content.data
                #themes.is_private = form.is_private.data
                db_sess.commit()
                return redirect('/')
            else:
                abort(404)
        return render_template('theme.html',
                               title='Редактирование темы',
                               form=form
                               )

    @app.route('/theme_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def themes_delete(id):
        db_sess = db_session.create_session()
        themes = db_sess.query(Themes).filter(Themes.id == id,
                                          Themes.user == current_user
                                          ).first()
        messages = db_sess.query(Messages).filter(Messages.theme_id == id)
        if themes:
            db_sess.delete(themes)
            for i in messages:
                db_sess.delete(i)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')




    app.run()

if __name__ == '__main__':
    main()
