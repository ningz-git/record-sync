# -*- coding:utf-8 -*-

# author: zhangning

import traceback
import time

class myProcess(object):
    def __init__(self, mysql_sel, oracle_ins, logger, interval, retail_id, table_name_sel, table_name_ins, column_name, sel_prefix, ins_prefix, row_number):
        self.mysql_sel = mysql_sel
        self.oracle_ins = oracle_ins
        self.logger = logger
        self.interval = interval
        self.retail_id = retail_id
        self.table_name_sel = table_name_sel
        self.table_name_ins = table_name_ins
        self.column_name = column_name
        self.sel_prefix = sel_prefix
        self.ins_prefix = ins_prefix
        self.row_number = row_number

    def push(self):
        while True:
            try:
                sql = "select max(%s) id from %s.%s where retail_id=%s" % (self.column_name, self.ins_prefix, self.table_name_ins, self.retail_id)
                res = self.oracle_ins._getOne(sql)
                if res[0] is None:
                    _max_id = 0
                else:
                    _max_id = res[0]
                sql = self.mysql_sel._getSelectSQL(self.sel_prefix+'.'+self.table_name_sel, self.column_name, _max_id, self.row_number)
                res = self.mysql_sel._getALL(sql)
                _records = len(res)
                for i in res:
                    # sql = self.oracle_ins._getInsertSQL(self.ins_prefix + '.' + self.table_name_ins, i)
                    # print sql
                    # self.oracle_ins._insertOne(sql, i.values())
                    self.oracle_ins._insertOne(self.oracle_ins._getInsertSQL(self.ins_prefix+'.'+self.table_name_ins, i), i.values())
                self.oracle_ins._conn.commit()

                # print "Max id of %s.%s is %s, insert %s records into %s.%s !" % (self.ins_prefix, self.table_name_ins, _max_id, _records, self.ins_prefix, self.table_name_ins)
                self.logger.info("Max id of %s.%s is %s, insert %s records into %s.%s !" % (self.ins_prefix, self.table_name_ins, _max_id, _records, self.ins_prefix, self.table_name_ins))
            except Exception as e:
                logger_info = 'mysql --- execute sql error:\n%s' % (traceback.format_exc())
                self.logger.error(logger_info)
            finally:
                time.sleep(self.interval)