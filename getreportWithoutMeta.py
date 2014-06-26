#!/usr/local/bin/python
# coding: utf-8
# BEGIN kludge from http://stackoverflow.com/questions/5109970/linux-python-encoding-a-unicode-string-for-print and https://wiki.python.org/moin/PrintFails
import sys, codecs, locale;
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);
# END KLUDGE
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

  del tags_hash["detailsmissing"]
  del tags_hash["offtopic"]
  del tags_hash["notafirefoxproblem"]
  del tags_hash["questiondeleted"]
  del tags_hash["dupe"]
  del tags_hash["developerquestion"]
  del tags_hash["devicecompat"]
  del tags_hash["desktopquestion"]
  del tags_hash["addonsproblem"]

  sorted_array_of_tuples = sorted(tags_hash.items(), key=lambda tag:tag[1])
  sorted_array_of_tuples.reverse()
  for tuple in sorted_array_of_tuples[:20]:
    print "1. %s:%d" % (tuple[0], tuple[1])

def get_details(start_date, end_date):
  for question in feedback_collection.find(\
    { "$and" : [ {"created_at": {"$gte": start_date,\
                     "$lte": end_date}},\
                 ]}).sort("created_at", 1):
    created_at = question["created_at"]
    tags_str = ", ".join(question["tags"])
    #print >> sys.stderr, "title", question['title']
  
    print '1. **%s** [%s](%s "%s"), %s' % \
      (created_at.strftime("%a %b %d %Y %I:%m %p"),\
       question["title"][0],\
       question["url"],\
       question["first_p"],\
       tags_str
     )
def get_verbatims(start_date, end_date):
  for question in feedback_collection.find(\
    { "$and" : [ {"created_at": {"$gte": start_date,\
                     "$lte": end_date}},\
                 ]}).sort("created_at", 1):
    if "verbatim" in question:
      print "1. [%s](%s)" % (question["verbatim"], question["url"])

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
print "#SUMO Forum Support Report  %s/%s/%s-%s/%s/%s" %(start_yy, start_mm, start_dd, end_yy, end_mm, end_dd)
print "##Tag Summary"
get_top_tags(start_date, end_date)
print "\n##Verbatims"
get_verbatims(start_date, end_date)
print "\n##Details"
get_details(start_date, end_date)


