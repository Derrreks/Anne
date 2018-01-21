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
    """Display the home page"""
    return flask.render_template('index.html')


@application.route('/start/', methods=['GET', 'POST'])
def start():
    """Start the annotations"""
    userid = flask.request.form['userid']
    return flask.redirect(flask.url_for('annotate_abstract', userid=userid))


@application.route('/annotate_abstract/<userid>/', methods=['GET'])
def annotate_abstract(userid):
    """Display the abstract for annotation"""
    art = anne.get_next_article()
    if not art or 'abstract' not in art.get_extra():
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.render_template('article.html',
                                     userid=userid,
                                     id=art.id_,
                                     title=art.title,
                                     text=art.get_extra()['abstract'],
                                     outcome=art.get_extra()['outcome'],
                                     intervention=art.get_extra()['intervention'],
                                     comparator=art.get_extra()['comparator'],
                                     options=config.options_abstract,
                                     article_path=art.get_extra()['path'])


@application.route('/annotate_full/<userid>/<article_path>', methods=['GET'])
def annotate_full(userid, article_path):
    """If the abstract could not be annotated, display the full text"""
    art = anne.get_next_article(next_file=article_path)

    if not art:
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.render_template('full_article.html',
                                     userid=userid,
                                     id_=art.id_,
                                     tabs=art.text,
                                     outcome=art.get_extra()['outcome'],
                                     intervention=art.get_extra()['intervention'],
                                     comparator=art.get_extra()['comparator'],
                                     options=config.options_full,
                                     article_path=article_path)


@application.route('/submit/', methods=['POST'])
def submit():
    """Submits the article id with all annotations"""
    # grab all the info we want to save from post request
    userid = flask.request.form['userid']
    id_ = flask.request.form['id']
    selected = flask.request.form['selection']

    if selected == 'Cannot tell based on the abstract':
        return flask.redirect(flask.url_for('annotate_full',
                                            userid=userid,
                                            article_path=flask.request.form['article_path']))

    annotations = json.loads(flask.request.form['annotations'])

    # put all annotations into a string and then use ... as a delimiter
    annotation_str = ''
    for a in annotations:
        annotation_str += a + "..."

    anne.submit_annotation([id_, selected, annotation_str])

    return flask.redirect(flask.url_for('annotate_abstract',
                                            userid=userid))


@application.route('/finish/', methods=['GET'])
def finish():
    """Only go to this if there are no more articles to be annotated"""
    return flask.render_template('finish.html')


@application.route('/results/', methods=['GET'])
def results():
    """Display the annotations"""
    return anne.get_results()


if __name__ == '__main__':
    application.run(debug=True)
