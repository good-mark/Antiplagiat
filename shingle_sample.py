# -*- coding: UTF-8 -*-
from operator import itemgetter
import hashlib
import codecs
import os
import sqlite3

SHINGLE_LEN = 10

class Database:
    def __init__(self):
        pass
    def create(self):
        ''' Для заданного хэша храним имя файла, из которого он был получен, и смещение внутри этого файла '''
        #self.db = {}
        self.db = sqlite3.connect('C:\Antiplagiat\my_db.sqlite')
        self.cur = self.db.cursor()
        #self.cur.execute('CREATE TABLE inde (shingle TEXT NOT NULL, documentName VARCHAR(100) NOT NULL, id INTEGER NOT NULL)')
        #self.db.commit()

    def put(self, key, value):
        '''if key in self.db:
            self.db[key].append(value)
        else:
            self.db[key] = [value]'''
        params = (str(key), value[0], value[1])
        self.cur.execute('INSERT INTO inde(shingle, documentName, id) VALUES(?,?,?)', params)
        self.db.commit()

    def find(self, key):
        '''if key in self.db.keys():
            return self.db[key]
        else:
            return []'''
        key_str = str(key)
        self.cur.execute('SELECT documentName, id FROM inde WHERE shingle=(?)', (key_str, ))
        result = self.cur.fetchall()
        return result


class Antiplagiat:
    def __init__(self):
        self.db = Database()
        self.db.create()


    ''' 
    Для входящей последовательности слов генерирует шингл, возвращает множество хэшей от шингла. 
    '''
    def generate_shingle(self, source):
        out = [] 
        for i in range(len(source) - (SHINGLE_LEN - 1)):
            out.append (hashlib.md5(' '.join( [x for x in source[i:i + SHINGLE_LEN]] )).hexdigest())

        return out

    ''' 
    Добавляет заданный файл в индекс. 
    '''
    def add_file_to_index(self, filename):
        with open(filename, 'r') as fin:
            text = fin.read()
            sh = self.generate_shingle(self.canonize(text))
            for inner_index, shingle in enumerate(sh):
                # Для заданного хэша храним имя файла, из которого он был получен, и смещение внутри этого файла
                self.db.put(shingle, [filename, inner_index])

    def add_files_to_index(self, path):
       for filename in os.listdir(path):
        fullname = os.path.join(path, filename)
        self.add_file_to_index(fullname)

    def find_shingle_in_index(self, shingle):
        return self.db.find(shingle)

    ''' 
    Вычисляет шингл для входящего файла и ищет совпадения в индексе. 
    Возвращает массив упоминаний: файл-источник, смещение в нем, смещение в исходном файле.
    Если упоминаний нет, возвращает пустой массив.
    '''
    def check(self, testfile):
        sources_list = []
        sources_by_doc = {}
        results_list = []
        with open(testfile, 'r') as fin:
            text = fin.read()
            sh = self.generate_shingle(self.canonize(text))
            for inner_index, shingle in enumerate(sh):
                result = self.find_shingle_in_index(shingle)
                if result == []:
                    continue
                else:
                    for match in result:
                        list(match).append(inner_index)
                        

                        ''' Добавляем в словарь, где ключом является имя документа-источника, 
                        чтобы удобно находить границы заимствования. '''
                        doc_name = match[0]
                        if doc_name in sources_by_doc:
                            sources_by_doc[doc_name].append([match[1], inner_index])
                        else:
                            sources_by_doc[doc_name] = [ [match[1], inner_index] ]

                    sources_list.extend(result)
                    #print result

        ''' Получаем для каждого документа нужные индексы '''
        for doc, coords in sources_by_doc.iteritems():
            sorted_coords = sorted(coords, key=itemgetter(0))
            #print 'coords: ', sorted_coords
            start_id_in_source = sorted_coords[0][0]
            start_id_in_test = sorted_coords[0][1]

            end_id_in_source = sorted_coords[0][0]
            end_id_in_test = sorted_coords[0][1]

            for idx, coord in enumerate(sorted_coords[1:]):
                #print 'iteration', coord, idx
                ''' Если отличаются на 1 '''
                if (coord[0] == sorted_coords[idx][0] + 1) and (idx != len(sorted_coords) - 2):
                    continue
                else:
                    end_id_in_source = coord[0]
                    end_id_in_test = coord[1]
                    results_list.append([doc, start_id_in_source, end_id_in_source + SHINGLE_LEN - 1, start_id_in_test, end_id_in_test + SHINGLE_LEN - 1])

                    start_id_in_source = coord[0]
                    start_id_in_test = coord[1]
            
        return results_list




    ''' 
    Предобрабатывает входящий текст: делит на токены, убирает стоп-слова. 
    Возвращает последовательность слов входящего текста без стоп-слов.
    ''' 
    def canonize(self, source):
        stop_symbols = '.,!?:;-\n\r()'

        stop_words = []

        return ( [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in stop_words)] )





def main():
    checker = Antiplagiat()
    #checker.add_files_to_index('C:\Antiplagiat\corpora_test')
    print checker.check('C:\Antiplagiat\plagiat_test\plagiat.txt')
    print '!!!'
    print checker.check('C:\Antiplagiat\plagiat_test\plagiat_partial.txt')




if __name__ == "__main__":
    main()

if __name__ == '__build__':
    raise Exception
