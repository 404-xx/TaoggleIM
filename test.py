#!/usr/bin/env python
# coding=utf-8

import re
import taobao

#ITEM_TEMPLATE="""%s 
#价格: ￥ %s  运费: %s 元  所在地: %s  30天售出 %d 件 
#%s 

#"""

TAOBAOKE_ITEM_TEMPLATE="""%s 
价格: ￥ *_%s_* 详情: %s 

"""

SEARCH_MORE_TEAMPLE=("更多请查看: %s")

def getOneItem():
  item = taobao.get(method = 'taobao.item.get', 
                    fields = 'title', 
                    nick = 'bjlibin', 
                    iid = '463cddf3f6b444921bc53e906ecaeb6e')
  return item

def searchItems(keyword):
  return taobao.get(method = 'taobao.items.get', 
                    fields = 'iid,title,nick,pic_url,cid,price,type,delist_time,post_fee,score,volume,location', 
                    q = keyword,
                    page_no='1',
                    page_size='5')
                    
def searchItemsByTaobaoke(keyword):
  return taobao.get(method = 'taobao.taobaoke.items.get', 
                    fields = 'click_url,title,price,commission', 
                    keyword = keyword,
                    nick = '淘江山更淘美人',
                    is_guarantee = 'true',
                    sort = 'credit_desc',
                    page_no='1',
                    page_size='10')
                    
def searchItemsURLByTaobaoke(keyword):
  return taobao.get(method = 'taobao.taobaoke.listurl.get',q=keyword,nick='淘江山更淘美人',outer_code='test')

def formatTitle(content):
  return re.sub(r'\<span.+\>(.+)\<.+\>', r'*_\1_*', content)
                    
def parseSearchResult(dataList):
  return "".join([TAOBAOKE_ITEM_TEMPLATE % (formatTitle(i["title"]), i["price"], i["click_url"],) for i in dataList])
 
if __name__ == "__main__":
  #print getOneItem()
  searchResult = searchItemsByTaobaoke("iPhone")
  #print searchResult["taobaokeItems"]
  print parseSearchResult(searchResult["taobaokeItems"])
  
  #searchResult = searchItemsURLByTaobaoke("iPhone")
  #print searchResult["taobaokeItems"][0]["list_url_by_q"]