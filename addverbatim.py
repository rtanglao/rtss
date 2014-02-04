#!/usr/local/bin/python
# coding: utf-8
#rtanglao-09392:rt-sumo-python-hacks rtanglao$ echo $LANG
# en_CA.UTF-8
# BEGIN kludge from http://stackoverflow.com/questions/5109970/linux-python-encoding-a-unicode-string-for-print and https://wiki.python.org/moin/PrintFails
import sys, codecs, locale;
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);
# END KLUDGE
# usage: ./addverbatim.py 324234 "djkd skjdfs"


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


def addverbatim(id, verbatim):
  print >> sys.stderr, "in ADDVERBATIM, id:",\
    id, " verbatim:", verbatim
  existing_question =  feedback_collection.find_one({"id" : id})
  if existing_question:
    print >> sys.stderr, "EXISTING QUESTION id:", id
    existing_question["verbatim"] = verbatim
    feedback_collection.update({"id":id}, existing_question)
    print >> sys.stderr, "UPDATED QUESTION id:", id
  else:
    print >> sys.stderr, "UNKNOWN QUESTION id:", id
  return

for line in sys.stdin:
  print >> sys.stderr, "id and verbatim:", line
  line = line.lower().split()
  id = int(line[0])
  verbatim = " ".join(line[1:])
  addverbatim(id, verbatim)

