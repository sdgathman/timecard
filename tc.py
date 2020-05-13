#!/usr/bin/python
#
# Simple timecard command

import sqlite3
import time
import sys
import os

DBNAME = os.path.expanduser('~/.timecard/timecards.sqlite')
WEEKDAYS = ('mon','tue','wed','thu','fri','sat','sun')
MONTHS = ('jan','feb','mar','apr','may','jun',
	  'jul','aug','sep','oct','nov','dec')
PERSONAL = set((
	'bed','break','shower','homeserver','lunch','marty','bank','dinner',
	'breakfast','mishi','movie','store','farm', 'nap', 'youngmen', 'mow',
	'church', 'gathman', 'seaman', 'hospital', 'cleaning', 'political',
	'sabbath', 'accounting', 'library', 'f19'
	))


def today_at(tod=None):
    now = time.time()
    if tod:
      t = time.localtime(now)
      ctod = t[3]*100 + t[4]
      if tod > ctod:
        t = time.localtime(now - 24*60*60)
      t = list(t)
      t[3] = tod//100
      t[4] = tod%100
      now = time.mktime(t)
    return now

def thispast_at(dow,tod,now=None):
    if not now:
      now = time.time()
    t = time.localtime(now)
    ctod = t.tm_hour*100 + t.tm_min
    cdow = t.tm_wday
    dow = WEEKDAYS.index(dow.lower())
    if dow < cdow: dow += 7
    t = time.localtime(now - (7-dow+cdow)*24*60*60)
    t = list(t)
    t[3] = tod//100
    t[4] = tod%100
    return time.mktime(t)

def last_at(ts,now=None):
    if not now:
      now = time.time()
    t1 = time.localtime(now)
    y = time.strftime('%Y',t1)
    t = time.strptime(ts+'/'+y,'%H%M%b%d/%Y')
    if time.mktime(t) > now:
      y = int(y)-1
      t = time.strptime('%s/%4d'%(ts,y),'%H%M%b%d/%Y')
    ts = time.mktime(t)
    assert ts < now
    return ts

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

  def bills(self,client):
    c = self.conn.cursor()
    c.execute('''select timein,comment from timecard
    	where user = ? and proj like ? order by timein''',
    	[self.user,'BILL-'+client])
    return [(r['timein'],r['comment']) for r in c]

  def detail(self,daysprev=0,filterClient=None,start_time=None):
    c = self.conn.cursor()
    if not start_time:
      start_time = today_at(0200)-daysprev*24*60*60
    if daysprev >= 7 and daysprev <= 14:
      end_time = start_time + 7*24*60*60
    else:
      end_time = time.time()
    c.execute('''select rowid,proj,user,host,timein,timeout,comment
    	from timecard
    	where user = ? and timein between ? and ? order by timein''',
    	[self.user,start_time,end_time])
    lr = None
    for r in c:
      if lr and (not filterClient or client(lr['proj']) == filterClient):
	d = {}
	d['rowid'] = lr['rowid']
	d['proj'] = lr['proj']
	d['timein'] = lr['timein']
	d['time'] = r['timein'] - lr['timein'] 
	d['comment'] = lr['comment']
	yield d
      lr = r
    if lr and (not filterClient or client(lr['proj']) == filterClient):
      d = {}
      d['rowid'] = lr['rowid']
      d['proj'] = lr['proj']
      d['timein'] = lr['timein']
      d['time'] = end_time - lr['timein'] 
      d['comment'] = lr['comment']
      yield d

  def list(self,daysprev=0):
    for r in self.detail(daysprev):
      print '%-18s %s %8.2f %s' % (
      	r['proj'],time.ctime(r['timein']),r['time']/3600.0,r['comment'])

  def summary(self,daysprev=0):
    s = {}
    for r in self.detail(daysprev):
      proj = r['proj']
      s[proj] = s.get(proj,0.0) + r['time']
    return s

  def punch_in(self,proj,comment='',tod=None):
    if tod:
      if tod.isdigit():
	now = today_at(int(tod))
      elif tod[-2:].isdigit():
        now = last_at(tod)
      else:
	now = thispast_at(tod[-3:],int(tod[:-3]))
    else:
      now = time.time()
    print tod,time.ctime(now)
    cur = self.conn.execute('begin immediate')
    try:
      r = proj,self.user,self.host,now,None,comment
      cur.execute('''insert into 
          timecard(proj,user,host,timein,timeout,comment)
          values(?,?,?,?,?,?)''', r)
      self.conn.commit()
    finally:
      cur.close();

def client(proj):
  "return personal, bms, unilit"
  a = proj.split('-')
  if a[0] in PERSONAL: return 'personal'
  if proj.startswith('bms'): return 'bms'
  if proj in PERSONAL: return 'personal'
  return 'unilit'

def clientReport(seq=0,client='bms'):
  with Timecard(DBNAME,'stuart') as tc:
    if seq:
      seq = -1 - int(seq)
    else:
      seq = -1
    bills = tc.bills(client)
    if bills:
      last_bill,comment = bills[seq]
    else:
      last_bill,comment = None,None
    s = {}
    print "last bill:",time.ctime(last_bill)
    for r in tc.detail(filterClient=client,start_time=last_bill):
      proj = r['proj']
      s[proj] = s.get(proj,0.0) + r['time']
      print '%-18s %s %8.2f %s' % (
      	proj,time.ctime(r['timein']),r['time']/3600.0,r['comment'])
    tot = 0
    for proj,secs in s.items():
      tot += secs
      print '%-18s %8.2f' % (proj,secs / 3600.0)
    print 'total',tot/3600.0

def istod(s):
  """True if s is a time specifier like HHMM or HHMMwww
  >>> istod('abc')
  False
  >>> istod('1234')
  True
  >>> istod('1030Mon')
  True
  >>> istod('1550Dec12')
  True
  """
  if s.isdigit(): return True
  if s[:-3].isdigit() and s[-3:].lower() in WEEKDAYS: return True
  if s[:-5].isdigit() and s[-2:].isdigit()	\
  	and s[-5:-2].lower() in MONTHS: return True
  return False

def help():
  print """
Usage:	tcf -c<client>		# list transactions for client
	tcf -<num> 		# list transactions for <num> days prev
	tcf HHMM proj [desc]	# add transition for proj at specific time
	tcf HHMMwww proj [desc]	# add transition for proj at previous weekday
	tcf HHMMmmmdd proj [desc] # add transition for proj at previous date
	tcf proj [desc]		# add transition for proj at current time
"""
  try:
    import doctest, tc
    return doctest.testmod(tc)
  except: pass

if __name__ == '__main__':
  argv = sys.argv[1:]
  if argv and argv[0].startswith('-'):
    opt = argv[0]
    argv = argv[1:]
    if opt.startswith('-c'):
      clientReport(opt[2:])
      sys.exit(0)
    if opt in ('-h','-?'):
      help()
      sys.exit(2)
    daysprev = -int(opt)
  else:
    daysprev = 0
  if argv:
    if len(argv) > 1 and istod(argv[0]):
      tod = argv[0]
      argv = argv[1:]
    else:
      tod = None
    proj = argv[0]
    comment = ' '.join(argv[1:])
    with Timecard(DBNAME,'stuart') as tc:
      tc.punch_in(proj,comment,tod=tod)
  else:
    with Timecard(DBNAME,'stuart') as tc:
      tc.list(daysprev)
      s = {}
      for proj,secs in tc.summary(daysprev).items():
        c = client(proj)
        print '%-8s %-18s %8.2f' % (c,proj,secs / 3600.0)
	s[c] = s.get(c,0) + secs
      print
      for c,secs in s.items():
        print '%-8s %-18s %8.2f' % ('TOTAL',c,secs / 3600.0)