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
    """Display the home page"""
    return flask.render_template('index.html')


@application.route('/start/', methods=['GET', 'POST'])
def start():
    """Start the annotations"""
    userid = flask.request.form['userid']
    if (userid is None or userid == ''):
        userid = 'anon'
    return flask.redirect(flask.url_for('annotate_abstract', userid=userid,
                                                id_ = anne.get_next_file()))


@application.route('/annotate_abstract/<userid>/<id_>/', methods=['GET'])
def annotate_abstract(userid, id_ = None):
    """Display the abstract for annotation"""
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
                                     outcome = art.get_extra()['outcome'],
                                     intervention = art.get_extra()['intervention'],
                                     comparator = art.get_extra()['comparator'],
                                     options = config.options)


@application.route('/annotate/<userid>/', methods=['GET'])
def annotate(userid):
    """Always grabs a random article and displays the full text"""
    art = anne.get_next_article()
    if not art:
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.render_template('article.html',
                                 userid=userid,
                                 id=art.id_,
                                 title=art.title,
                                 text=art.text)


@application.route('/annotate_full/<userid>/<id_>/', methods=['GET'])
def annotate_full(userid, id_ = None):
    """Grabs a specified article and displays the full text"""
    if id_ is None:
        art = anne.get_next_article()
    else:
        art = anne.get_next_article(id_)

    if not art:
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.render_template('full_article.html',
                                     userid = userid,
                                     id_ = art.id_,
                                     tabs = art.text,
                                     outcome = art.get_extra()['outcome'],
                                     intervention = art.get_extra()['intervention'],
                                     comparator = art.get_extra()['comparator'],
                                     options = config.options_full)


@application.route('/submit/', methods=['POST'])
def submit():
    """Submits the article id with all annotations"""
    # grab all the info we want to save from javascript code
    userid = flask.request.form['userid']
    id_ = flask.request.form['id']
    selected = flask.request.form['selection']
    annotations = eval(flask.request.form['annotations'])

    # put all annotations into a string and then use ... as a delimiter
    annotation_str = ''
    for a in annotations:
        annotation_str += a + "..."

    anne.submit_annotation([id_, selected, annotation_str])

    # if the person can't tell just based off the abstract
    if (selected == 'Cannot tell based on the abstract'):
        global last_path
        return flask.redirect(flask.url_for('annotate_full',
                                           userid=userid, id_= last_path))
    elif (selected == ''): # if they haven't selected anything, do nothing
        return None
    else: # otherwise go to the next abstract
        return flask.redirect(flask.url_for('annotate_abstract',
                                            userid=userid,
                                            id_ = anne.get_next_file()))


@application.route('/finish/', methods=['GET'])
def finish():
    """Only go to this if there are no more articles to be annotated"""
    return flask.render_template('finish.html')


@application.route('/results/', methods=['GET'])
def results():
    """Display the annotations"""
    return anne.get_results()


if __name__ == '__main__':
    application.run()
