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

utc=pytz.UTC

start_yy = sys.argv[1]
start_mm = sys.argv[2]
start_dd = sys.argv[3]
end_yy = sys.argv[4]
end_mm = sys.argv[5]
end_dd = sys.argv[6]

search_end_url_str = "https://support.mozilla.org/en-US/search?q=&num_voted=0&num_votes=&asked_by=&answered_by=&q_tags=&product=mobile&created=1&created_date="+ end_mm + "%2F" + end_dd + "%2F" + end_yy + "&updated=0&updated_date=&sortby=2&a=1&w=2"

def insert_question(url, title, id, first_p, created_at):
  print >> sys.stderr, "in INSERT_question()"

  try:
    id_int = int(id)
  except:
    print >> sys.stderr, "NON INTEGER id:", id
    return
  
  question = {}
  question['tags'] = []
  question['url'] = url
  question['title'] = title
  question['id'] = id_int
  question['type'] = 'question'
  question['first_p'] = first_p
  question['created_at'] = created_at

  existing_question =  feedback_collection.find_one({"id" : id_int})
  if existing_question:
    print >> sys.stderr, "EXISTING QUESTION id:", id_int
    question['tags'] = existing_question['tags']
    feedback_collection.update({"id":id_int}, question)
    print >> sys.stderr, "UPDATED QUESTION id:", id_int
  else:
    print >> sys.stderr, "INSERTING QUESTION id:", id_int
    feedback_collection.insert(question)

  return

def scrape_support_questions(search_end_url_str):
  page = -1
  
  print >> sys.stderr, "url of search:", search_end_url_str
  start = dateutil.parser.parse(start_yy+"/" + start_mm + "/" + start_dd)
  start = utc.localize(start)
  print >> sys.stderr, "START:", start
  while True:
    page += 1
    if page != 0:
      search_end_url_str = search_end_url_str + "&page=" + str(page)
    else:
      search_end_url_str = search_end_url_str 

    print >> sys.stderr, "calling URLOPEN on:", search_end_url_str
    response = urllib2.urlopen(search_end_url_str)
    html_search_page = response.read()
    soup = BeautifulSoup(html_search_page)
    all_h3 = soup.find_all('h3')
    for child in soup.find_all('h3'):
      for l in child.children:
        rel_link = l.get('href')
        title = l.contents
        try:
          url = "https://support.mozilla.org/en-US" + rel_link
          print >> sys.stderr, "PAGE_URL:", url
          m = re.search('(?<=questions\/)\w+', url)
          id = m.group(0)
          print >> sys.stderr, 'url of QUESTION:', url, ' id:', id
          response = urllib2.urlopen(url)
          print >> sys.stderr, "HTTP GET url of QUESTION"
          html = response.read()
          s2 = BeautifulSoup(html)
          main_content  = s2.findAll("div", { "class" : "main-content" })
          if type (main_content[0].p.contents[0]) is bs4.element.NavigableString:
            first_p  = main_content[0].p.contents[0].rstrip()
          else:
            if type(main_content[0].p.contents[0].contents) is list:
              first_p = main_content[0].p.contents[0].contents[0].rstrip()
            else:
              first_p  = main_content[0].p.contents[0].contents.rstrip()
          first_75 = first_p[:75] + (first_p[75:] and u'...')
          time_str = s2.find_all('time')[0]['datetime']
          print >> sys.stderr, "time_str:", time_str
          t2 = dateutil.parser.parse(time_str) 
          print >> sys.stderr, "T2:", t2
          if (t2 < start):
            print >> sys.stderr, "EXITING because current time is less than start time"
            return
          else:
            date = t2.strftime("%a %b %d %Y %I:%m %p")
            print >> sys.stderr, 'first75:', first_75, 'title[0]:', title[0]
            m  = re.search('([^?]*)', url)
            non_crufty_url = m.group(0) 
            insert_question(non_crufty_url, title, id, first_p, t2)
        except Exception:
          print formatExceptionInfo()
          pass
        except:
          print >> sys.stderr, "EXCEPTION"
          pass

scrape_support_questions(search_end_url_str)

