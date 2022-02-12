#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import time
import json
import requests
import urllib

reg = re.compile(r'\<article class="article__bd"\>(.*)\</article\>')
imgreg = re.compile('<img src="(.*?)" class="ke_img"')
imgnamereg = re.compile('/([0-9a-z]+?\.(jpg|png))')


Headers = {
'Connection': 'keep-alive',
'Cache-Control': 'max-age=0',
'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': '"macOS"',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Sec-Fetch-Site': 'none',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-User': '?1',
'Sec-Fetch-Dest': 'document',
'Accept-Language': 'zh-CN,zh;q=0.9',
'Cookie': 's=bt129mjjya; cookiesu=291642222816193; device_id=be9e1q8c59efefe20da9b89282d9f195; MONITOR_WEB_ID=ad7ed0aa-212e-44f3-828a-7551b59b1253; Hm_lvt_1db88642e346389874251b5a1eded6e3=1643034817,1644647376; xq_a_token=b5b273e7b466ede1c7cef9667b5bc416eb1eea43; xqat=b5b273e7b466ede1c7cef9667b5bc416eb1eea43; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjE1MjMxODA5NjYsImlzcyI6InVjIiwiZXhwIjoxNjQ3MjQwMzc2LCJjdG0iOjE2NDQ2NDgzNzYyOTIsImNpZCI6ImQ5ZDBuNEFadXAifQ.ZFnOJIsuStaRuMTOYH3Dp98yRDZmeILrVpiZ2RKvVOPtbtWh41BfBwd_oN1ZHkx9QFIF43fgyBWtX9xwNfRaGNnxg3lXlLVxyCp2dUxmr0POZ1GTYaE9XjyS1CQN2ixkAIVbd2HqVI71urcVxOinef9O6EA_pmJqfi1A0b2Bge66-lJXjmYNolrZ9bfwS9p0BA5zlxZn4GVnds4TEQMpZzWnAiH_l0Q3HvNagd0sfHLqk50KA_Ja2UxzT7qfo2csGJq9-sUdGO6Fxd0PF_04hkIhckkM5Qgml2seut6DTPFu5Q49Rcuc0XR5QrVsmxEIa16DVmZasWniGUT0V2v91A; xq_r_token=91accbe2f7d0f63bf22996d13bcfa000ffc0b1fd; xq_is_login=1; u=1523180966; snbim_minify=true; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1644649049; acw_tc=2760826116446492148872815eb57f58096d5a84420c4d24292f1d18e8711e'
		}

Temp = '''<html>
    <head>
    <meta name="generator"
    content="HTML Tidy for HTML5 (experimental) for Windows httpss://github.com/w3c/tidy-html5/tree/c63cc39" />
    <meta https-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{0}</title>
    <link href="../static/styles/reset.css" rel="stylesheet" type="text/css" />
    <link href="../static/styles/index/style.css" rel="stylesheet" type="text/css" />
    </head>
    <body>

    <div class="page">
		<table style="text-align: center;" width="90%"  align="center" border="0" cellpadding="2" cellspacing="2">
                    <tbody>
                        <tr>
                            <td style="width: auto; text-align: center;"><a href="https://xueqiu.com">
								<img src="../images/favicon.png" alt="xueqiu"></a></td>
                            <td style="width: auto; text-align: center;"><h1>{0}</h1>
								<p><a href="{1}">{2}</a>&nbsp;&nbsp;{3}</p></td>
                        </tr>
					</tbody>
				</table>
				<hr noshade="noshade" />
				<div class="main box">
				{4}</div>
				<a href="{6}">{5}</a>
				<hr />
				<div id="quotes" class="clearfix" style="text-align: center;">
					<p>Copyright &copy 1996-2014 SINA Corporation All Rights Reserved.</p>
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
	imgfolder = os.path.join(basedir,'images')
	if not os.path.exists(imgfolder):
		os.mkdir(imgfolder)
	for blogitem in blogs:
		target = blogitem['target']
		lastedit = u'最后修改于：%s'%blogitem['lastedit']
		author = str(blogitem['user_id'])
		authorfolder = os.path.join(basedir,author)
		if not os.path.exists(authorfolder):
			os.mkdir(authorfolder)
		title = blogitem['title']
		if title=='':
			title = blogitem['description'][0:16]
		author = blogitem['author']
		userlink = 'https://xueqiu.com/%s'% blogitem['user_id']
		createdtime = blogitem['created']
		url = 'https://xueqiu.com%s'%target
		page = createdtime + "_" + target.split('/')[-1]+'.html'
		blogpath = os.path.join(authorfolder, page)
		if not os.path.exists(blogpath):
			r = requests.get(url, headers = Headers)
			raw =  r.text
			art = re.search(reg, raw)
			if not art:
				continue
			article = art.group(0)
			imglist = [item[-1] for item in re.findall(imgreg, article)]
			for imgurl in imglist:
				try:
					imgname = '../images/'+re.search(imgnamereg, imgurl).group(1)
					imgpath = os.path.join(imgfolder,imgname)
					article = article.replace(imgurl, imgname)
					urllib.urlretrieve(imgurl, imgpath, cbk)
					time.sleep(2)
				except Exception as e:
					print e

			html = Temp.format(title.encode('utf-8'), userlink,author.encode('utf-8'),createdtime,article.encode('utf-8'),lastedit.encode('utf-8'), url)
			fileobj = open(blogpath,'w')
			fileobj.write(html)
			fileobj.close()

def blogList(id):
	_url = "https://xueqiu.com/v4/statuses/user_timeline.json?page={1}&user_id={0}"
	first = _url.format(id,1)
	r = requests.get(first, headers = Headers)
	jdata = json.loads(r.text, encoding = 'utf-8')
	maxpage = jdata['maxPage']+1
	for page in xrange(1,maxpage):
		print "page %d" % page
		blogs = []
		url = _url.format(id,page)  # page from 1
		r = requests.get(url, headers = Headers)
		jdata = json.loads(r.text, encoding = 'utf-8')
		articles = jdata['statuses']
		for article in articles:
			creattime = time.strftime("%Y-%m-%d",time.localtime(float(article['created_at']/1000)))
			lastedit = creattime if article['edited_at'] == None else time.strftime("%Y-%m-%d",time.localtime(float(article['edited_at']/1000)))
			blogs.append({'target':article['target'],'title':article['title'],'created':creattime,'lastedit':lastedit,'user_id':article['user_id'],'author':article['user']['screen_name'],'description':article['description']})
		saveBlog(blogs)
		time.sleep(1)

if __name__ == '__main__':
	idlist = ['uid']
	for id in idlist:
		blogs = blogList(id)
