import flask
import json

import annotator
import article
import config
import reader
import writer


application = flask.Flask(__name__)

anne = annotator.Annotator(reader.get_reader(config.reader)(**config.reader_params),
                           writer.get_writer(config.writer)(**config.writer_params))


@application.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

@application.route('/start/', methods=['GET', 'POST'])
def start():
    userid = flask.request.form['userid']
    return flask.redirect(flask.url_for('annotate', user_id=userid))

@application.route('/annotate/<user_id>', methods=['GET'])
def annotate(user_id):
    art = anne.get_next_article()
    if not art:
        return flask.redirect(flask.url_for('finish'))
    return flask.render_template('article.html',
                                 userid=user_id,
                                 id=art.id_,
                                 title=art.title,
                                 text=art.text,
                                 extra=art.get_extra(),
                                 options=config.options)

@application.route('/submit/', methods=['POST'])
def submit():
    user_id = flask.request.form['userid']
    article_id = flask.request.form['id']
    annotations = flask.request.form['annotations']
    annotations = json.loads(annotations)
    selection = flask.request.form['selection']
    anne.submit_annotation(user_id=user_id, article_id=article_id, annotations=annotations, selection=selection)
    return flask.redirect(flask.url_for('annotate', user_id=user_id))

@application.route('/finish/', methods=['GET'])
def finish():
    return flask.render_template('finish.html')

@application.route('/results/', methods=['GET'])
def results():
    return anne.get_results()


if __name__ == '__main__':
    application.run()
