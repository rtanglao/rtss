#!/usr/local/bin/python
# coding: utf-8
#rtanglao-09392:rt-sumo-python-hacks rtanglao$ echo $LANG
# en_CA.UTF-8
# BEGIN kludge from http://stackoverflow.com/questions/5109970/linux-python-encoding-a-unicode-string-for-print and https://wiki.python.org/moin/PrintFails
import sys, codecs, locale;
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);
# END KLUDGE
# usage: ./s-sumo-kb-1-day.py 2014 01 06 2014 01 07

from bs4 import BeautifulSoup
import bs4
import urllib2
import time
import sys
from datetime import datetime
import dateutil.parser
import pytz
import traceback
import re
import os
from pymongo import MongoClient
import webbrowser

mongo_pw = os.environ.get('MONGO_PASSWORD')
print >> sys.stderr, "MONGO_PASSWORD:", mongo_pw
mongo_user = os.environ.get('MONGO_USER')
print >> sys.stderr, "MONGO_USER:", mongo_user
mongo_port = os.environ.get('MONGO_PORT')
print >> sys.stderr, "MONGO_PORT:", mongo_port
mongo_host = os.environ.get('MONGO_HOST')
print >> sys.stderr, "MONGO_HOST:", mongo_host

if mongo_host is None:
  client = MongoClient()
else:
  client = MongoClient(mongo_host, int(mongo_port))

feedback_db = client['feedback']

if mongo_user is not None:
  client.feedback_db.authenticate(mongo_user, mongo_password)

feedback_collection = feedback_db['feedback_collection']


def formatExceptionInfo(maxTBlevel=5):
  cla, exc, trbk = sys.exc_info()
  excName = cla.__name__
  try:
    excArgs = exc.__dict__["args"]
  except KeyError:
    excArgs = "<no args>"
  excTb = traceback.format_tb(trbk, maxTBlevel)
  return (excName, excArgs, excTb)


def find_untagged_questions(start_date, end_date):
  print >> sys.stderr, "in FIND_untagged_question, start:",\
    start_date, " end:", end_date

  for question in feedback_collection.find(\
    { "$and" : [ {"created_at": {"$gte": start_date,\
                     "$lte": end_date}},\
                 {"type": "question"},\
                 {"tags": []}]}):
    print question["id"]
    webbrowser.open_new_tab(question["url"])

  return


utc=pytz.UTC

start_yy = sys.argv[1]
start_mm = sys.argv[2]
start_dd = sys.argv[3]
end_yy = sys.argv[4]
end_mm = sys.argv[5]
end_dd = sys.argv[6]

start = dateutil.parser.parse(start_yy+ "/" + start_mm + "/" + start_dd) 
start_date = utc.localize(start)

end  = dateutil.parser.parse(end_yy + "/" + end_mm + "/" + end_dd + " 23:59:59") 
end_date = utc.localize(end)

find_untagged_questions(start_date, end_date)

