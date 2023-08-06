import glob
import os

from cbitmap import Bitmap
from tqdm import tqdm

from .config import database_default_path
from .logger import logger
from .util import green, str2number_u32


class Database:

    def __init__(self, path):
        self.path = path
        self.database = None
        self.name = os.path.splitext(os.path.basename(path))[0]
        self._open = False
    
    def open(self):
        if not self._open:
            self.database = Bitmap().load(self.path)
            self._open = True
        return self

    def close(self):
        if self._open:
            delattr(self, 'database')
            self.database = None
        self._open = False

    def get_name(self):
        return self.name

    def isin(self, query_kmer):
        if not self._open:
            self.open()
        return self.database.get(str2number_u32(query_kmer))

    def __del__(self):
        self.close()

    def __str__(self):
        return 'Database<%s>' % self.name

class KmerDatabase:
    """ 创建一个参考序列（ref）的kmer查询数据库 """
    def __init__(self, path=database_default_path):
        patt = os.path.join(path, '*.db')
        self.path = glob.glob(patt)
        for p in self.path:
            if not os.path.exists(p):
                raise FileNotFoundError('文件%s未找到' % p)

        self._database = [
            Database(p)
            for p in self.path
        ]
        self._all_database = [
            d.get_name()
            for d in self._database
        ]

        self._using_database = []

    def __str__(self):
        logger.info('Find %d database: ' % len(self._database))
        logger.info('**********************')
        for index, database in enumerate(self._database):
            logger.info('%d. %s' % (index+1, database))
        logger.info('**********************')
        return ''

    def list_all_database(self):
        return self._all_database

    def list_active_database(self):
        return self._using_database

    def database_count(self):
        return len(self._database)

    def get_database_path_by_name(self, name):
        return os.path.join(database_default_path, name + '.db')

    def create_database_name(self, name):
        new_database = self.get_database_path_by_name(name)
        if os.path.exists(new_database):
            # raise ValueError('Name <%s> has already exists, please give a new one.' % name)
            return False
        return new_database

    def delete_database(self, name):
        """ 根据一个名字删除数据库 """
        database_path = self.get_database_path_by_name(name)
        if os.path.exists(database_path):
            os.remove(database_path)

    def list_database_by_name(self, name):
        return [
            i
            for i in glob.glob(os.path.join(database_default_path, '*db'))
            if name in os.path.basename(name)
        ]

    def _batch_find(self, query_kmers):
        """ 批量查找 """
        ret = {}
        using_database = [
            d
            for d in self._database 
            if d.get_name() in self._using_database
        ]
        if not using_database:return []

        for kmer in query_kmers:
            ret[kmer] = []

        for database in using_database:
            database.open()
            logger.info('Search from database: %s' % green(database.name))
            for kmer in tqdm(query_kmers, total=len(query_kmers)):
                h = database.isin(kmer)
                if h:
                    ret[kmer].append(database.get_name())
            # TODO
            # 要不要先把需要的数据都先合并成一个bitmap？
            database.close()
        return ret

    def batch_find(self, query_kmers):
        if not query_kmers:
            return {}
        return self._batch_find(query_kmers)

    def using_database_count(self):
        return len(self._using_database)

    def use(self, database_name):
        if database_name not in self._all_database:
            logger.error('%s database does not exist.' % database_name)
            exit(1)
        self._using_database.append(database_name)
        self._using_database = list(set(self._using_database))
