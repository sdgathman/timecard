#!/usr/bin/python
#
# Simple timecard command

import sqlite3
import time
import sys
import os

DBNAME = os.path.expanduser('~/.timecard/timecards.sqlite')

class Timecard(object):

  def __init__(self,dbname,user,host=None):
    self.user = user
    if host:
      self.host = host
    else:
      self.host = os.uname()[1]
    self.conn = sqlite3.connect(dbname)
    self.conn.row_factory = sqlite3.Row
    try:
      self.conn.execute('''create table timecard(
        proj text, user text, host text,
        timein timestamp, timeout timestamp, comment text,
        primary key (timein,user,host))''')
    except: pass

  def __enter__(self): return self
  def __exit__(self,*x): self.close(); return False

  def close(self):
    self.conn.close()

  def punch_in(self,proj,comment=''):
    now = time.time()
    cur = self.conn.execute('begin immediate')
    try:
      r = proj,self.user,self.host,now,None,comment
      cur.execute('''insert into 
          timecard(proj,user,host,timein,timeout,comment)
          values(?,?,?,?,?,?)''', r)
      self.conn.commit()
    finally:
      cur.close();

if __name__ == '__main__':
  if len(sys.argv) > 1:
    proj = sys.argv[1]
    comment = ' '.join(sys.argv[2:])
    with Timecard(DBNAME,'stuart') as tc:
      tc.punch_in(proj,comment)
