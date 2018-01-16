import abc
import json
import csv


class Writer(object, metaclass=abc.ABCMeta):
    """Write annotation information.

    A base class for writing annotation information
    out after the article has been annotated by
    the user.
    """

    @abc.abstractmethod
    def submit_annotation(self, article_id, annotations):
        """Submits an annotation."""
        raise NotImplementedError('Method `submit_annotation` must be defined')

    @abc.abstractmethod
    def get_results(self):
        """Returns results of project."""
        raise NotImplementedError('Method `get_results` must be defined')


class CSVWriter(Writer):
    """Write to CSV files.

    A `Writer` implementation that writes annotation
    information out to a CSV file. If multiple annotations
    for a single article are provided, they are entered
    in separate columns. If provided, a selection will try
    to be saved as well.

    Writes to CSV in form:
    user_id, article_id, (selection), annotation1, annotation2, ...
    """

    def __init__(self, write_file):
        self.write_file = write_file

    def submit_annotation(self, data):
        with open(r'out.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)

    def get_results(self):
        with open(self.write_file, 'r') as csvfile:
            lines = csvfile.readlines()
        return '<br><br>'.join(lines)


class SQLiteWriter(Writer):
    """Write to a SQLite database.

    A `Writer` implementation to support writing
    annotation data out to a database. If multiple
    annotations exist for one Article, they will
    be entered as separate rows in the database. If
    provided, a selection will try to be saved as well.

    Expects columns of form:
    user_id, article_id, (selection), annotation
    """

    def __init__(self, db_file, table):
        self.db_file = db_file
        self.table = table
        self.conn = sqlite3.connect(self.db_file)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()

    def submit_annotation(self, user_id, article_id, annotations, selection=None):
        selection_text = ''
        if selection:
            selection_text = ', {0}, '.format(selection)

        query = 'INSERT INTO {0} VALUES({1}, {2},{3}{4})' \
                .format(self.table, user_id, article_id, selection_text, annotation)
        for annotation in annotations:
            self.cursor.execute(query.format(annotation))
        self.cursor.commit()

    def get_results(self):
        self.cursor.execute('SELECT * FROM {0}'.format(self.table))
        rows = self.cursor.fetchall()
        return json.dumps(rows)


def get_writer(writer):
    options = {
        'csv': CSVWriter,
        'sql': SQLiteWriter,
    }
    if writer in options:
        return options[writer]
    raise Exception('{0} not a valid writer.'.format(writer))
