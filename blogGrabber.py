#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import time
import json
import requests
import urllib

_url = "http://xueqiu.com/v4/statuses/user_timeline.json?user_id=2821861040&page={0}&type=1"
reg = re.compile(r'<h4 class="status-title">(.*)</h4>(.*)</script>(.*)<!-- pdf--></div>')
imgreg = re.compile('<img class="ke_img" src="(.*?)" />')

Headers = {
		'Accept-Encoding':'gzip, deflate, sdch',
		'Accept-Language':'en-US,en;q=0.8',
		'Cache-Control':'no-cache',
		'Connection':'keep-alive',
		'Cookie':'bid=75681dc6ba15e098e48baef01f8a42e4_i5d8ufwr; xq_a_token=500c9d0017cb45d945defada18cb5e454e36b055;', 
		'Host':'xueqiu.com',
		'Pragma':'no-cache',
		'RA-Sid':'DE49C559-20141120-021811-7a9e85-d30286',
		'RA-Ver':'2.8.7',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'
		}
		
def saveBlog(blogs):
	currentpath  = os.path.realpath(__file__)
	basedir = os.path.dirname(currentpath)
	for blogitem in blogs:
		target = blogitem['target']
		title = blogitem['title']
		url = 'http://xueqiu.com/%s'%target
		r = requests.get(url, headers = Headers)	
		raw =  r.text
		blogFolder = os.path.join(basedir, title)
		if not os.path.exists(blogFolder):
			os.mkdir(blogFolder)
		article = re.search(reg, raw).group(3)
		imglist = re.findall(imgreg, article)
		# print imglist
		for idx, imgurl in enumerate(imglist):
			try:
				imgpath = os.path.join(blogFolder,str(idx)+'.jpg')
				urllib.urlretrieve(imgurl, imgpath)
				time.sleep(2)
				# r = requests.get(imgurl, headers = Headers)
				# with open(imgpath, "wb") as code:
					# code.write(r.content)
					# time.sleep(1)
			except Exception as e:
				print e
		# http://xqimg.imedao.com/14b5f1c56344053fc69d62d8.png!custom.jpg
		# print imglist
		#fileobj = open(local,'w')
		#fileobj.write(li.encode('utf-8'))
		#fileobj.close()
	
def blogList(url):	
	url = url.format(1)
	r = requests.get(url, headers = Headers)
	jdata = json.loads(r.text, encoding = 'utf-8')
	maxpage = jdata['maxPage']
	blogs = []
	for page in xrange(maxpage):
		url = _url.format(page+1)  # page from 1
		r = requests.get(url, headers = Headers)
		jdata = json.loads(r.text, encoding = 'utf-8')
		articles = jdata['statuses']		
		for article in articles:
			blogs.append({'target':article['target'],'title':article['title']})
	return blogs

blogs = blogList(_url)
saveBlog(blogs)
