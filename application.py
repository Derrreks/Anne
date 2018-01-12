import flask
import json

import annotator
import article
import config
import reader
import writer

global last_path
application = flask.Flask(__name__)

anne = annotator.Annotator(reader.get_reader(config.reader)(**config.reader_params),
                           writer.get_writer(config.writer)(**config.writer_params))


@application.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

@application.route('/start/', methods=['GET', 'POST'])
def start():
    userid = flask.request.form['userid']
    return flask.redirect(flask.url_for('annotate_abstract', userid=userid,
                                        id_ = anne.get_next_file()))

@application.route('/annotate_abstract/<userid>/<id_>/', methods=['GET'])
def annotate_abstract(userid, id_ = None):
    if id_ is None or id_ == 'None':
        return flask.redirect(flask.url_for('annotate', userid=userid))

    art = anne.get_next_article(id_)
    if not art or not('abstract' in art.get_extra()):
        return flask.redirect(flask.url_for('finish'))
    else:
        global last_path; last_path = art.get_extra()['path']
        return flask.render_template('article.html',
                              userid=userid,
                              id= art.id_,
                              title = art.title,
                              text = art.get_extra()['abstract'],
                              options = config.options)

"""
Always grabs a random article and displays the full text.
"""
@application.route('/annotate/<userid>/', methods=['GET'])
def annotate(userid):
    art = anne.get_next_article()

    if not art:
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.render_template('article.html',
                                 userid=userid,
                                 id=art.id_,
                                 title=art.title,
                                 text=art.text)

"""
Grabs a specified article and displays the full text.
"""
@application.route('/annotate_full/<userid>/<id_>/', methods=['GET'])
def annotate_full(userid, id_ = None):
    if id_ is None:
        art = anne.get_next_article()
    else:
        art = anne.get_next_article(id_)

    if not art:
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.render_template('article.html',
                                 userid=userid,
                                 id=art.id_,
                                 title=art.title,
                                 text=art.text)


@application.route('/submit/', methods=['POST'])
def submit():
    userid = flask.request.form['userid']
    selected = flask.request.form['selection']
    id_ = flask.request.form['id']
    if (selected == 'Cannot tell based on the abstract'):
        global last_path
        return flask.redirect(flask.url_for('annotate_full',
                                            userid=userid, id_=last_path))
    elif (selected == ''):
        return None
    else:
        annotations = flask.request.form['annotations']
        annotations = json.loads(annotations)
        anne.submit_annotation(id_, annotations)
        return flask.redirect(flask.url_for('annotate', userid=userid))

@application.route('/finish/', methods=['GET'])
def finish():
    return flask.render_template('finish.html')

@application.route('/results/', methods=['GET'])
def results():
    return anne.get_results()


if __name__ == '__main__':
    application.run()
