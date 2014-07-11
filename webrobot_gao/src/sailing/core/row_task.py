# -*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing
import codecs
import os

'''
Created on 2013-7-16

文件的每一个，作为一个需要执行的任务。
@author: deonwu
'''


class RowTask(object):
    
    def __init__(self, file_path, done_path=None):
        self.task_path = file_path
        if done_path:
            self.done_path = done_path
        else:
            self.done_path = "%s.done" % self.task_path
        
        if not os.path.isfile(file_path):
            raise Exception("Not found task file:%s" % file_path)
        
        self._writer = None
        self.done_list = self._load_done_data()
            
    def task_list(self):
        return self._next_lines()
    
    def done_task(self, row):
        self._get_done_writer().write("%s\n" % row)
        self.done_list.append(row)
        self._get_done_writer().flush()
    
    @property
    def done_count(self):
        return len(self.done_list)
    
    def _next_lines(self):
        with closing(codecs.open(self.task_path, 'r', "utf-8")) as links:
            for l in links:
                #comment or empty line
                if l.startswith("#") or not l.strip():continue
                #header
                if l[0].isupper():continue
                l = l.strip()
                if l in self.done_list: continue
                yield l    
    
    def _get_done_writer(self):
        if self._writer is None:
            self._writer = codecs.open(self.done_path, 'a', "utf-8")    
        return self._writer
    
    def _load_done_data(self):
        data = []
        
        if not os.path.isfile(self.done_path):
            return data
        
        with closing(codecs.open(self.done_path, 'r', "utf-8")) as links:
            for l in links:
                #comment or empty line
                if l.startswith("#") or not l.strip():continue
                #header
                if l[0].isupper():continue
                l = l.strip()
                data.append(l)
        return data    
    
    def close(self):
        if self._writer is not None:
            self._writer.close()
    
    
    