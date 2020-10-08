import os

from whoosh.index import create_in, open_dir


class LanguageIndex(object):
    index = None
    # writer = None  # keep a writer for bulk updates

    def __init__(self, base_path, lang, schema):
        self.base_path = base_path
        self.lang = lang
        self.schema = schema

    def _get_path(self):
        return os.path.join(self.base_path, self.lang)

    def clear(self):
        '''create index from scratch; creates a writer too.'''

        index_path = self._get_path()
        if not os.path.exists(index_path):
            os.makedirs(index_path)
        self.index = create_in(index_path, self.schema)

        writer = self.index.writer()
        ## optimize analyzer for batch updates
        # analyzer = writer.schema['content'].format.analyzer
        # analyzer.cachesize = -1
        # analyzer.clear()
        from whoosh.analysis.morph import StemFilter
        analyzer = writer.schema['content'].analyzer
        for item in analyzer.items:
            if isinstance(item, StemFilter):
                item.cachesize = -1
                item.clear()
        writer.commit()
        # self.writer = writer

    def load(self):
        '''load an existing index'''
        self.index = open_dir(self._get_path())
        return self.index
        # return open_dir(self._get_path())

    def get_writer(self):
        # if not self.writer:
        #     self.writer = self.index.writer()
        # return self.writer
        return self.index.writer()

    # def close_writer(self):
    #     if self.writer:
    #         self.writer.close()
    #         self.writer = None
