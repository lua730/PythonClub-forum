import flask
from flask import jsonify

from . import db_session
from .themes import Themes
from .messages import Messages

blueprint = flask.Blueprint(
    'themes_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/themes')
def get_themes():
    db_sess = db_session.create_session()
    themes = db_sess.query(Themes).all()
    messages = db_sess.query(Messages).all()
    for i in themes:
        i.messages = []


    for i in messages:
        print(i.theme_id)
        for j in range(len(themes)):
            if themes[j].id == i.theme_id:
                themes[j].messages.append({"content":i.content, "user_id":i.user_id, "created_date":i.created_date})


    return jsonify(
        {
            'themes':
                [item.to_dict(only=('title', 'content', 'user_id', 'created_date', 'messages'))
                 for item in themes]
        }
    )