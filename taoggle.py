#!/usr/bin/env python
# coding=utf-8

import os
import re
import datetime
import logging
import taobao
import googl
import wsgiref.handlers
from google.appengine.api import xmpp
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.ereporter import report_generator
#from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers


WELCOME_MSG = ("Hi, 我是淘宝搜索机器人—— *淘哥* 。"
               "想买什么, 让哥来淘, 您再挑！"
               "发消息告诉我您想要购买的 *宝贝名称* , 我会立刻呈现淘宝网上关于该宝贝的搜索结果给您。"
               "还不快来试试手气? PS: 输入 */help* 可以查看详细的帮助信息哦！\n\n"
               "若您有任何疑问或好的建议可以在Twitter上给我留言. - http://twitter.com/l404")
HELP_MSG = ("哥淘的不是宝, 是乐趣~ %s")
WAIT_MSG = "正在帮您搜索 *%s*, 请稍候... \n\n"
TAOBAOKE_ITEM_TEMPLATE = ("_%s_. %s ￥_%s_ 元 %s \n\n")
SEARCH_MORE_TEAMPLE = (">>上淘宝网搜索 *%s* : %s")
TAOBAOKE_NICK = '淘江山更淘美人'


class GooURL(db.Model):
  item_id = db.StringProperty(required=True)
  url = db.StringProperty(required=True)
  created_at = db.DateTimeProperty(auto_now_add=True)


class KeyContent(db.Model):
  keyword = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created_at = db.DateTimeProperty(auto_now_add=True)


class Taoggle():
  @staticmethod
  def search(keyword):
    #items=db.GqlQuery("SELECT * FROM KeyContent")
    #for item in items.fetch(100):
    #  item.delete()
    utf8_keyword = keyword.encode('utf-8')
    item = db.GqlQuery("SELECT * FROM KeyContent WHERE keyword=:1", keyword.lower()).get()
    if item:
      result = item.content
    else:
      search_result = taobao.get(method = 'taobao.taobaoke.items.get', \
                                 fields = 'iid,click_url,title,price', \
                                 keyword = utf8_keyword, \
                                 nick = TAOBAOKE_NICK, \
                                 is_guarantee = 'true', \
                                 sort = 'credit_desc', \
                                 page_no = '1', \
                                 page_size = '10')
      search_results = sorted(search_result["taobaokeItems"], key=lambda i: float(i["price"]))
      result = Taoggle._parse_search_result(search_results)
      list_result = taobao.get(method='taobao.taobaoke.listurl.get', q=keyword, nick=TAOBAOKE_NICK, outer_code='tg')
      list_url = list_result["taobaokeItems"][0]["list_url_by_q"]
      result += SEARCH_MORE_TEAMPLE % (utf8_keyword, googl.shortening(list_url),)
      item = KeyContent(keyword = keyword.lower(), content = result.decode('utf-8'))
      item.put()
    return result
  
  @staticmethod
  def _parse_search_result(dataList):
    l = []
    counter = 0
    for i in dataList:
      counter += 1
      gurl = db.GqlQuery("SELECT * FROM GooURL WHERE item_id=:1", i["id"]).get()
      if gurl:
        shorted_url = gurl.url
      else:
        shorted_url = googl.shortening(i["click_url"])
        gurl = GooURL(item_id=i["id"], url=shorted_url)
        gurl.put()
      e = TAOBAOKE_ITEM_TEMPLATE % (counter, Taoggle._format_title(i["title"]), i["price"], shorted_url.encode('utf-8'),)
      l.append(e)
    return "".join(l)
  
  @staticmethod
  def _format_title(content):
    return re.sub(r'\<span.+\>(.+)\<.+\>', r' *\1* ', content)

class XmppHandler(xmpp_handlers.CommandHandler):
  """Handler class for all XMPP activity."""
  
  def unhandled_command(self, message=None):
    message.reply(WELCOME_MSG)
    
  def text_message(self, message=None):
    keyword = message.arg.strip()
    message.reply(WAIT_MSG % keyword.encode('utf-8'))
    response = Taoggle.search(keyword)
    message.reply(response)


class SweepingItemsHandler(webapp.RequestHandler):
  def get(self):
    this_time_yesterday = datetime.datetime.now() - datetime.timedelta(hours=24)
    items = KeyContent.all().filter("created_at <", this_time_yesterday)
    for item in items:
      item.delete()


class SweepingURLsHandler(webapp.RequestHandler):
  def get(self):
    this_time_last_month = datetime.datetime.now() - datetime.timedelta(days=30)
    urls = GooURL.all().filter("created_at <", this_time_last_month)
    for url in urls:
      url.delete()


def main():
  app = webapp.WSGIApplication([
      ('/tasks/sweeping/items', SweepingItemsHandler),
      ('/tasks/sweeping/urls', SweepingURLsHandler),
      ('/_ah/xmpp/message/chat/', XmppHandler),
      ], debug=True)
  wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
  main()
