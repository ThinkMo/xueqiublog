#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import time
import json
import requests
import urllib

reg = re.compile(r'<h4( class="status-title")?>(.*)</h4>(.*)</script>(.*)<!-- pdf--></div>')
imgreg = re.compile('<img class="ke_img" src="(.*?)"')
imgnamereg = re.compile('/([^.]*?\.(jpg|png))')
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

Temp = '''<html>
    <head>
    <meta name="generator"
    content="HTML Tidy for HTML5 (experimental) for Windows https://github.com/w3c/tidy-html5/tree/c63cc39" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{0}</title>
    <link href="../../static/styles/reset.css" rel="stylesheet" type="text/css" />
    <link href="../../static/styles/index/style.css" rel="stylesheet" type="text/css" />
    </head>
    <body>
	
    <div class="page">
		<table style="text-align: center;" width="90%"  align="center" border="0" cellpadding="2" cellspacing="2">
                    <tbody>
                        <tr>
                            <td style=width: auto; text-align: center;"><a href="http://xueqiu.com">
								<img src="../../static/images/favicon.png" alt="xueqiu"></a></td>
                            <td style=width: auto; text-align: center;"><h1>{0}</h1>
								<p><a href="{1}">{2}</a>&nbsp;&nbsp;{3}</p></td>
                        </tr>
					</tbody>
				</table>
				<hr noshade="noshade" />
				<div class="main box">	  
				{4}</div>
				<hr />
				<div id="quotes" class="clearfix" style="text-align: center;">
					<p>Copyright &copy 1996-2014 SINA Corporation All Rights Reserved. </p>
				</div>
			</div>
		</body>
	</html>'''


def cbk(blocknum, blocksize, totalsize):
    per = 100.0 * blocknum * blocksize / totalsize  
    if per > 100:  
        per = 100  
    print '%.2f%%' % per  
		
def saveBlog(blogs):
	currentpath  = os.path.realpath(__file__)
	basedir = os.path.dirname(currentpath)	
	for blogitem in blogs:
		target = blogitem['target']
		foldername = target.split('/')[-1]
		title = blogitem['title']
		
		if title=='':
			title = blogitem['description'][0:16]
		author = blogitem['author']
		authorfolder = os.path.join(basedir,author)
		if not os.path.exists(authorfolder):			
			os.mkdir(authorfolder)
		userlink = 'http://xueqiu.com/%s'% blogitem['user_id']
		createdtime = blogitem['created']
		url = 'http://xueqiu.com/%s'%target		
		blogFolder = os.path.join(authorfolder, foldername)		
		if not os.path.exists(blogFolder):
			os.mkdir(blogFolder)
			r = requests.get(url, headers = Headers)	
			raw =  r.text
			article = re.search(reg, raw).group(4)
			imglist = re.findall(imgreg, article)
			articlepath = os.path.join(blogFolder, title+'.html')
			
			for idx, imgurl in enumerate(imglist):
				try:
					imgname = re.search(imgnamereg, imgurl).group(1)
					imgpath = os.path.join(blogFolder,imgname)
					article = article.replace(imgurl, imgname)
					urllib.urlretrieve(imgurl, imgpath, cbk)
					time.sleep(2)
				except Exception as e:
					print e

			html = Temp.format(title.encode('utf-8'), userlink,author.encode('utf-8'),createdtime,article.encode('utf-8'))
			fileobj = open(articlepath,'w')
			fileobj.write(html)
			fileobj.close()
	
def blogList(id):
	_url = "http://xueqiu.com/v4/statuses/user_timeline.json?user_id={0}&page={1}&type=2"
	first = _url.format(id,1)	
	r = requests.get(first, headers = Headers)
	jdata = json.loads(r.text, encoding = 'utf-8')
	maxpage = jdata['maxPage']+1
	blogs = []
	for page in xrange(1,maxpage):
		url = _url.format(id,page)  # page from 1
		r = requests.get(url, headers = Headers)
		jdata = json.loads(r.text, encoding = 'utf-8')
		articles = jdata['statuses']		
		for article in articles:
			timestamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(article['created_at']/1000)))
			blogs.append({'target':article['target'],'title':article['title'],'created':timestamp,'user_id':article['user_id'],'author':article['user']['screen_name'],'description':article['description']})
	return blogs

if __name__ == '__main__':
	idlist = ['6341375334','2821861040'] #6341375334, 2821861040
	for id in idlist:
		blogs = blogList(id)
		saveBlog(blogs)
