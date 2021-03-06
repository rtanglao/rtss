#!/usr/local/bin/python
# coding: utf-8
#rtanglao-09392:rt-sumo-python-hacks rtanglao$ echo $LANG
# en_CA.UTF-8
# BEGIN kludge from http://stackoverflow.com/questions/5109970/linux-python-encoding-a-unicode-string-for-print and https://wiki.python.org/moin/PrintFails
import sys, codecs, locale;
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);
# END KLUDGE
# usage: ./rename_tag.py ux ui_issues

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
import fileinput

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


def rename_tag(old_tag, new_tag):
  print >> sys.stderr, "in RENAME_TAG old tag:", old_tag,\
    " new tag:", new_tag
  for question in feedback_collection.find():
    for t in question["tags"]:
      print  >> sys.stderr, "tag: ", t
      if t == old_tag:
        print >> sys.stderr, "TAG MATCH FOUND", old_tag, " renaming to", new_tag
        question["tags"].remove(old_tag)
        question["tags"].append(new_tag)
        feedback_collection.update({"id":question["id"]}, question)
      else:
        print >> sys.stderr, "t:", t, "does not match old tag:", old_tag

old_tag = sys.argv[1].lower()
new_tag = sys.argv[2].lower()
rename_tag(old_tag, new_tag)

