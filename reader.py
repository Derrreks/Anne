import abc
import csv
import os
import random
import sqlite3
import xml.etree.ElementTree as ET
from get_file_description import get_file_description
import numpy as np

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
        self.file_description = get_file_description()


    def _get_next_file(self):
        """Returns an XML file from `path` if exists"""
        try:
            paths = os.listdir(self.path)
            if ('desktop.ini' in paths): # issue with internal works of windows
                paths.remove('desktop.ini')
            next_file = random.choice(paths)
        except:
            return None
        return next_file

    def _get_ids(self, article_meta):
        """Return the proper ids associated with this specific XML file

        @param article_meta the XML element that holds the article title.
        """
        ids = article_meta.findall('article-id')
        id_ = None # the number associated with the xml
        for id in ids:
            if 'pub-id-type' in id.attrib and id.attrib['pub-id-type'] == 'pmid':
                id_ = id.text

        return id_

    def _get_title(self, article_meta):
        """Return the title of the article.

        @param article_meta the XML element that holds the article title.
        """
        title_xml = article_meta.find('title-group').find('article-title')
        title = ET.tostring(title_xml, encoding='utf8', method='text').decode('utf-8')
        return title


    def _get_sections(self, body):
        """Return the article split into sections.
        It will return an array of pairs, with a given pair having a first
        entry of the title, and the second entry containing the actual
        text of that section.

        @param body represents the whole article.
        """
        arr = []
        title = ""
        paragraph = ""
        children = body.getchildren()
        for i in range(len(children)):
            child = children[i]
            if (child.tag == 'sec'):
                sub_sec = self._get_sections(child)
                arr.append(sub_sec)
            elif (child.tag == 'title'):
                title = ET.tostring(child, method = 'text', encoding = 'utf8').decode('utf-8')
            else:
                paragraph += ET.tostring(child).decode('utf-8')

        if (title == '' and len(arr) > 0):
            return arr
        elif (len(arr) > 0):
            return [title, arr]
        else:
            return [title, paragraph]


    def _get_full_text(self, body):
        """Return all of the text in an XML file.

        @param body represents the main portion of the XML with the data.
        """
        text = ET.tostring(body).decode('utf-8')
        return text

    def _init_article_(self, next_file, article_meta, body):
        """Initialize the article to have the proper fields"""
        id_ = self._get_ids(article_meta) # PMC1784771
        title = self._get_title(article_meta)
        try:
            abstract = ET.tostring(article_meta.find('abstract').find('p')).decode('utf-8')
        except:
            abstract_sections = self._get_sections(article_meta.find('abstract'))
            abstract = ''
            for part in abstract_sections:
                abstract += part[1]

        if not(body is None):
            text = self._get_sections(body) #self._get_full_text(body)
            text.insert(0, ['Abstract', abstract])
        else:
            text = [['Abstract', abstract]]

        # store the path of this file
        art = article.Article(id_= id_, title=title, text=text)
        art.get_extra()['path'] = next_file

        file_data = self.file_description[int(id_)]
        sp_file_data = file_data[np.random.randint(len(file_data))]
        art.get_extra()['outcome'] = sp_file_data['outcome_name']
        art.get_extra()['comparator'] = sp_file_data['intervention1']
        art.get_extra()['intervention'] = sp_file_data['intervention2']

        # only get the abstract if the next_file is None or it doesn't exist
        if (not(abstract is None) and not(next_file is None)):
            art.get_extra()['abstract'] = abstract # add the abstract in

        return art

    def get_next_article(self, next_file=None):
        """Grabs a random XML article and displays it"""
        next_file = next_file or self._get_next_file()

        if not next_file:
            return None
        path_to_file =  self.path + '/' + next_file # the path to XML files
        et = ET.parse(path_to_file)
        root = et.getroot()

        front = root.find('front')
        article_meta = front.find('article-meta')
        body = root.find('body')

        try:
            art = self._init_article_(next_file, article_meta, body)
            return art
        except:
            return self.get_next_article()


def get_reader(reader):
    """Builder pattern for readers"""
    options = {
        'csv': CSVReader,
        'sql': SQLiteReader,
        'xml': XMLReader,
    }
    if reader in options:
        return options[reader]
    raise Exception('{0} not a valid reader.'.format(reader))
