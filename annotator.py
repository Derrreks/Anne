
class Annotator(object):
    """Annotate articles.

    The main object of the application. Takes a
    `Reader` and a `Writer,` and uses them to
    provide an interface for annotating articles
    and submitting their annotations.
    """

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    def get_next_article(self):
        return self.reader.get_next_article()

    def submit_annotation(self, id_, annotations):
        return self.writer.submit_annotation(id_, annotations)

    def get_results(self):
        return self.writer.get_results()