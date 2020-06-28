import numpy as np
import pandas as pd

from bs4 import BeautifulSoup as bs
import urllib.request as ur
import urllib.parse as up
import urllib.error as ue
import http.cookiejar as hc

import re
import gzip
import json

import time
import os
import socket

os.chdir(r'D:\program files\Python\Learn')
socket.setdefaulttimeout(30)

headers={
    'Host': 'bangumi.tv',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Sec-Fetch-Dest': 'document',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': ''
}
# 创建cookiejar对象
cj=hc.CookieJar()
# 根据cookiejar创建handler对象
hl=ur.HTTPCookieProcessor(cj)
# 根据handler创建opener对象
opener=ur.build_opener(hl)
pattern=re.compile(r'li id="item_(\d+)"')
subjectlist=[]
def update_cookie(cookie=str()):
    return cookie[:cookie.rfind('utmb=')]+cookie[cookie.rfind('utmb='):].split('.')[0]+'.'+str(int(cookie[cookie.rfind('utmb='):].split('.')[1])+1)+'.'+cookie[cookie.rfind('utmb='):].split('.')[2]+'.'+cookie[cookie.rfind('utmb='):].split('.')[3]
    def bangumidownload(start,end,subjectlist):
    for i in range(start,end+1):
        url='https://bangumi.tv/anime/browser?sort=rank&page=%d'%(i)
        print('downloading page',i)
        
        try_time=0
        while try_time<=5:
            try:
                r=ur.Request(url=url,headers=headers)
                response=opener.open(r) 
                break
            except Exception as e:
                try_time+=1
                headers['Cookie']=update_cookie(headers['Cookie'])
                print('retrying with cookie=',headers['Cookie'][cookie.rfind('utmb='):],try_time)
        else:
            raise Exception('Download Failed!!')
            
        content=response.read().decode()
        response.close()

        thispage=re.findall(pattern,content)
        
        subjectlist.extend(thispage)
bangumidownload(1,239,subjectlist)
with open(r'bangumi\subjectlist_0405.json','w') as fp:
    json.dump(subjectlist,fp)
bgmdb=[]
def bangumifulldownload(bgmsubjects):
    for i in bgmsubjects:
        url='https://bangumi.tv/subject/'+i
        print('downloading subject '+i)
        
        try_time=0
        while try_time<=5:
            try:
                r=ur.Request(url=url,headers=headers)
                response=opener.open(r) 
                break
            except Exception as e:
                try_time+=1
                headers['Cookie']=update_cookie(headers['Cookie'])
                print('retrying with cookie=',headers['Cookie'][headers['Cookie'].rfind('utmb='):],try_time)
        else:
            raise Exception('Download Failed!!')
            
        content=str(gzip.decompress(response.read()),'utf-8')
        response.close()

        soup=bs(content)
        mainWrapper=soup.find('div',class_='mainWrapper')
        name=soup.find('h1',class_='nameSingle')
        if mainWrapper==None or name==None:
            continue
        
        infobox=mainWrapper.find('ul',id='infobox')
        if infobox==None:
            continue
        infodict=dict()
        infodict.update({'subject':i,'原名':name.find('a').text if name.find('a')!=None else '',
                         '类型':name.find('small').text if name.find('small')!=None else ''})
        
        info=infobox.find_all('li')
        for each_info in info:
            kv=each_info.text.split(':',maxsplit=1)
            infodict.update({kv[0].strip():kv[1].strip()})
        
        tagWrapper=mainWrapper.find('div',class_='inner')
        if tagWrapper==None:
            continue
        tagtext=tagWrapper.select('.l span,a small')
        tags=[]
        for everytag in tagtext:
            tags.append(everytag.text)
        tags=' '.join(tags)
        infodict.update({'tags':tags})
        
        chartWrapper=mainWrapper.find('div',id='ChartWarpper')
        infodict.update({'votes':chartWrapper.find('span',property='v:votes').text})
        
        rating_list=[]
        for each_rater in chartWrapper.find_all('span',{'class':'count'}):
            rating_list.append(each_rater.text[1:-1])
        infodict.update({'ratings':rating_list})
            
        overall_score=0
        overall_vote=0
        for score in range(10,0,-1):
            overall_vote+=int(infodict['ratings'][10-score])
            overall_score+=score*int(infodict['ratings'][10-score])
        overall_score=overall_score/overall_vote
        infodict.update({'rating':str('%.3f'%(overall_score))})
        
        print(infodict)
        bgmdb.append(infodict)
bangumifulldownload(subjectlist)
with open(r'bangumi\bgmdb_0406.json','w') as fp:
    json.dump(bgmdb,fp)
bgmfulldb=pd.read_json(r'bangumi\bgmdb_0406.json')
indexs=bgmfulldb[~bgmfulldb.isna()].count().sort_values(ascending=False)[:60].index
bgmdb2=[]
# id org chs type othername episode production rater rate
for i in bgmdb:
    thisanime=[]
    
    for each_key in indexs:
        if each_key in i.keys():
            thisanime.append(i[each_key])
        else:
            thisanime.append('')
    
    bgmdb2.append(thisanime)
bgmdb2=pd.DataFrame(bgmdb2,columns=indexs)
bgmdb2.to_csv(r'bangumi\bgmdb2_0406.csv',index=False)        