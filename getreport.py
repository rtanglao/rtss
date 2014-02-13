#!/usr/local/bin/python
# coding: utf-8
import time
import sys
from datetime import datetime
import dateutil.parser
import pytz
import traceback
import re
import os
from pymongo import MongoClient

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

def get_top_tags(start_date, end_date):
  tags_hash = {}
  for question in feedback_collection.find(\
    { "$and" : [ {"created_at": {"$gte": start_date,\
                     "$lte": end_date}},\
                 ]}):
    for tag in question["tags"]:
      if tag in tags_hash:
        print >> sys.stderr, "INCREMENTING tag count for tag:", tag, "FROM ", tags_hash[tag], " by 1 to ", tags_hash[tag]+1

        tags_hash[tag] += 1
      else:
        print >> sys.stderr, "INITIALIZING tag count for tag:", tag
        tags_hash[tag] = 1
  print >> sys.stderr, "tags_hash:", tags_hash

  sorted_array_of_tuples = sorted(tags_hash.items(), key=lambda tag:tag[1])
  sorted_array_of_tuples.reverse()
  for tuple in sorted_array_of_tuples[:10]:
    print "1. %s:%d" % (tuple[0], tuple[1])

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

print "#Summary"
get_top_tags(start_date, end_date)

