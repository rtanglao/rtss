#!/usr/local/bin/python
# coding: utf-8
#rtanglao-09392:rt-sumo-python-hacks rtanglao$ echo $LANG
# en_CA.UTF-8
# BEGIN kludge from http://stackoverflow.com/questions/5109970/linux-python-encoding-a-unicode-string-for-print and https://wiki.python.org/moin/PrintFails
import sys, codecs, locale;
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);
# END KLUDGE

from bs4 import BeautifulSoup
import bs4
import urllib2
import time
import sys
from datetime import datetime
import dateutil.parser
yy = sys.argv[1]
mm = sys.argv[2]
dd = sys.argv[3]

page = 0
#url_str = "https://support.mozilla.org/en-US/search?q=&num_voted=0&num_votes=&asked_by=&answered_by=&q_tags=&product=mobile&created=1&created_date=01%2F07%2F2014&updated=0&updated_date=&sortby=2&a=1&w=2"
url_str = "https://support.mozilla.org/en-US/search?q=&num_voted=0&num_votes=&asked_by=&answered_by=&q_tags=&product=mobile&created=1&created_date="+ mm + "%2F" + dd + "%2F" + yy + "&updated=0&updated_date=&sortby=2&a=1&w=2"

print url_str

# response = urllib2.urlopen(sys.argv[1])
# html_search_page = response.read()
# soup = BeautifulSoup(html_search_page)
# all_h3 = soup.find_all('h3')
# for child in soup.find_all('h3'):
#     for l in child.children:
#         rel_link = l.get('href')
#         title = l.contents
#         try:
#             url = "https://support.mozilla.org/en-US" + rel_link
#             print >> sys.stderr, 'url of question:', url
#             response = urllib2.urlopen(url)
#             html = response.read()
#             s2 = BeautifulSoup(html)
#             main_content  = s2.findAll("div", { "class" : "main-content" })
#             if type (main_content[0].p.contents[0]) is bs4.element.NavigableString:
#                 first_p  = main_content[0].p.contents[0].rstrip()
#             else:
#                 if type(main_content[0].p.contents[0].contents) is list:
#                     first_p = main_content[0].p.contents[0].contents[0].rstrip()
#                 else:
#                     first_p  = main_content[0].p.contents[0].contents.rstrip()
#             first_75 = first_p[:75] + (first_p[75:] and u'..')
#             time_str = s2.find_all('time')[0]['datetime']
#             t2 = dateutil.parser.parse(time_str)
#             date = t2.strftime("%a %b %d %Y %I:%m %p")
#             print >> sys.stderr, 'first75:', first_75, 'title[0]:', title[0]
#             print '1. **%s** [%s](%s "%s")' % (date, title[0], url, first_75)
#         except:
#             pass

