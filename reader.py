import abc
import csv
import os
import random
import sqlite3
import xml.etree.ElementTree as ET

import article


class Reader(object, metaclass=abc.ABCMeta):
    """Read article information.

    A base class for providing article information
    to be annotated by the user.
    """

    @abc.abstractmethod
    def get_next_article(self):
        """Gets the next article to be annotated."""
        raise NotImplementedError('Method `get_next_article` must be defined')


class CSVReader(Reader):
    """Read from CSV files.

    A `Reader` implementation to support reading article data
    from a CSV file. Uses a buffer to preload a preset number
    of articles to speed up accessing the next article.
    """

    '''
    @param read_file represents a csv file location.
    '''
    def __init__(self, read_file, buffer_size=None):
        self.read_file = read_file

        self.buffer = []
        self.current_pos = 0
        if not buffer_size:
            with open(self.read_file, 'r') as csvfile:
                lines = csv.DictReader(csvfile)
                file_length = sum(1 for line in lines)
                buffer_size = max(file_length // 10, 100)
        self.buffer_size = buffer_size
        self._add_to_buffer()
        import pprint; pprint.pprint(self.buffer)

    def _add_to_buffer(self):
        with open(self.read_file, 'r') as csvfile:
            lines = csv.DictReader(csvfile)
            for i, line in enumerate(lines):
                if i < self.current_pos:
                    continue
                self.current_pos += 1
                self.buffer.append(line)

    def get_next_article(self):
        if not self.buffer:
            self._add_to_buffer()
        try:
            entry = self.buffer.pop(0)
        except IndexError:
            # we have gone through the entire file
            return None
        return article.Article(id_=entry['id'],
                               title=entry['title'],
                               text=entry['text'])


class SQLiteReader(Reader):
    """Read from a SQLite database.

    A `Reader` implementation to read articles from
    a SQLite database. Requires that there exist columns
    titled 'title' and 'text' and that the rows are
    uniquely id'd beginning at 0.
    """

    def __init__(self, db_file, table):
        self.db_file = db_file
        self.table = table
        self.conn = sqlite3.connect(self.db_file)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
        self.current_pos = 0

    def get_next_article(self):
        self.cursor.execute('SELECT title, text FROM {0} WHERE id={1}' \
                            .format(self.table, self.current_pos))
        articles = self.cursor.fetchall()
        if not articles or len(articles) != 1:
            return None
        art = article.Article(id_=self.current_pos,
                              title=articles[0][0],
                              text=articles[0][1])
        self.current_pos += 1
        return art


class XMLReader(Reader):
    """Read from XML files.

    A `Reader` implementation to read articles from XML files
    that are stored in a given path. Currently expects files to
    be of the form of an NLM article.
    """

    def __init__(self, path):
        self.path = path

    """
    Given the path that leads to a folder of ONLY XML files, the function
    will pick one and then return the name of it.
    """
    def _get_next_file(self):
        try:
            paths = os.listdir(self.path)
            if ('desktop.ini' in paths): # issue with internal works of windows
                paths.remove('desktop.ini')
            next_file = random.choice(paths)
        except IndexError as _:
            # Provided path has no files
            return None
        return next_file
    
    """
    Grabs a random XML article and displays it.
    """
    def get_next_article(self, next_file=None):
        next_file = next_file or self._get_next_file()
        if not next_file:
            return None
        path_to_file =  self.path + '/' + next_file
        et = ET.parse(path_to_file)
        root = et.getroot()
        
        front = root.find('front')
        article_meta = front.find('article-meta')

        ids = article_meta.findall('article-id')
        id_ = None # the number associated with the xml
        for id in ids:
            if 'pub-id-type' in id.attrib and id.attrib['pub-id-type'] == 'pmid':
                id_ = id.text

        title = article_meta.find('title-group').find('article-title').text
        body = root.find('body')
        abstract = ET.tostring(article_meta.find('abstract')).decode('utf-8')
        import pdb; pdb.set_trace()
        if body is None:
            return None
        text = ET.tostring(body).decode('utf-8')
        
        article = article.Article(id_=id_, title=title, text=text)
        return article


class ResearchReader(Reader):
    """Read from a combination of CSV/XML files.

    A custom reader to support research work.
    """

    def __init__(self, csv_file, path_to_xml_files):
        with open(csv_file, 'r') as f:
            self.entries = list(csv.DictReader(f))
        self.curr_idx = 0
        self.max_idx = len(self.entries) - 1
        self.xml_reader = XMLReader(path_to_xml_files)

    def get_next_article(self):
        if self.curr_idx > self.max_idx:
            return None

        entry = self.entries[self.curr_idx]
        self.curr_idx += 1

        art = self.xml_reader.get_next_article(entry['XML_file_names'])
        if art is None:
            return self.get_next_article()
        art.entry = entry
        return art


def get_reader(reader):
    options = {
        'csv': CSVReader,
        'sql': SQLiteReader,
        'xml': XMLReader,
        'research': ResearchReader
    }
    if reader in options:
        return options[reader]
    raise Exception('{0} not a valid reader.'.format(reader))
