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
import glob

os.chdir(r'D:\program files\Python\Spider')
socket.setdefaulttimeout(30)
cookie=''
headers={
    'Host': 'api.bilibili.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Accept':' application/json, text/plain, */*',
    'Sec-Fetch-Dest': 'empty',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Origin': 'https://www.bilibili.com',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.bilibili.com/anime/index/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie':cookie
}
# 创建cookiejar对象
cj=hc.CookieJar()
# 根据cookiejar创建handler对象
hl=ur.HTTPCookieProcessor(cj)
# 根据handler创建opener对象
opener=ur.build_opener(hl)
sspath=glob.glob('bilibili\\sslist*.json')[0]
mdpath=glob.glob('bilibili\\mdlist*.json')[0]
dtespath=glob.glob('bilibili\\dtesdict*.json')[0]
with open(sspath,'r') as fp:
    ssurls=json.load(fp)
ssurls=set(ssurls)
old_ssurls=ssurls.copy()
with open(mdpath,'r') as fp:
    mdlist=json.load(fp)
old_mdlist=mdlist.copy()
with open(dtespath,'r') as fp:
    dtesdict=json.load(fp)
def req(url,headers):
    try_time=0
    while try_time<=5:
        try:
            r=ur.Request(url=url,headers=headers)
            response=opener.open(r) 
            break
        except ue.HTTPError as e:
            print('Page Not found...skipped')
            break
        except Exception as e:
            try_time+=1
            print('retrying',try_time)
    else:
        raise Exception('Download Failed!!')
    return response
pattern=re.compile(r'https://www.bilibili.com/bangumi/play/ss\d+')
pattern2=re.compile(r'"title":"(.*?)"')
def ssdownload():
    for i in range(1,1000):
        url='https://api.bilibili.com/pgc/season/index/result?season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&order=5&st=1&sort=0&page='+str(i)+'&season_type=1&pagesize=20&type=1'
        print('downloading page='+str(i))
        
        response=req(url,headers)
        
        try:
            content=str(gzip.decompress(response.read()),'utf-8')
        except Exception as e:
            break
            
        response.close()
        
        titles=re.findall(pattern2,content)
        ssurl=re.findall(pattern,content)
        
        set_ssurl=set(ssurl)
        if set_ssurl.issubset(ssurls):
            break
        
        for i in range(len(ssurl)):
            ssurls.add(ssurl[i])
def ssdownload2():
    for i in range(1,1000):
        url='https://api.bilibili.com/pgc/season/index/result?season_version=-1&is_finish=-1&copyright=-1&season_status=-1&year=-1&style_id=-1&order=5&st=4&sort=0&page='+str(i)+'&season_type=4&pagesize=20&type=1'
        print('downloading page='+str(i))
        
        response=req(url,headers)
        
        try:
            content=str(gzip.decompress(response.read()),'utf-8')
        except Exception as e:
            break
            
        response.close()
        
        titles=re.findall(pattern2,content)
        ssurl=re.findall(pattern,content)
        
        set_ssurl=set(ssurl)
        if set_ssurl.issubset(ssurls):
            break
        
        for i in range(len(ssurl)):
            ssurls.add(ssurl[i])
ssdownload()
ssdownload2()
new_ssurls=list(ssurls.difference(old_ssurls))
headers={
    'Host': 'www.bilibili.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Sec-Fetch-Dest': 'document',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Referer': 'https://www.bilibili.com/anime/index/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie':cookie
}
mdpattern=re.compile('\d+')
summary_dict={}
def mddownload():
    for each_ssurl in new_ssurls:
        print('downloading item='+str(new_ssurls.index(each_ssurl)))
        
        try_time=0
        httperror=False
        while try_time<=5:
            try:
                r=ur.Request(url=each_ssurl,headers=headers)
                response=opener.open(r) 
                break
            except ue.HTTPError as e:
                httperror=True
                print('Page Not found...skipped')
                break
            except Exception as e:
                try_time+=1
                print('retrying',try_time)
        else:
            raise Exception('Download Failed!!')
        
        if httperror:
            continue
        
        content=str(gzip.decompress(response.read()),'utf-8')
        response.close()
        
        soup=bs(content)
        
        mdlist.append(re.search(mdpattern,str(soup.find('div', id='media_module').find('a'))).group())
        summary_dict.update({mdlist[-1]:soup.find('span',class_='absolute').text})
mddownload()
notfoundmd=[5558,27059477,4762714,102512,139612,102552,3048]
mdlist=[int(i) for i in mdlist]
mdlist.extend(notfoundmd)
mdlist=list(set(mdlist))
mdlist=sorted(mdlist)
new_mdlist=list(set(mdlist).difference(set(old_mdlist)))
headers={
    'Host': 'api.bilibili.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Accept':' application/json, text/plain, */*',
    'Sec-Fetch-Dest': 'empty',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Origin': 'https://www.bilibili.com',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.bilibili.com/anime/index/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie':cookie
}
bilidb=list()
for i in mdlist:
    url='https://api.bilibili.com/pgc/review/user?media_id='+str(i)
    r=ur.Request(url=url,headers=headers)
    response=opener.open(r)
    content=str(response.read(),'utf-8')
    mdjson=json.loads(content)
    
    if 'result' in mdjson.keys():
        if 'media' in mdjson['result'].keys():
            url='https://api.bilibili.com/pgc/web/season/stat?season_id='+str(mdjson['result']['media']['season_id'])
            r=ur.Request(url=url,headers=headers)
            response=opener.open(r)
            content=str(response.read(),'utf-8')
            mdjson2=json.loads(content)
            mdjson['result'].update(mdjson2['result'])
    
    bilidb.append(mdjson['result'] if 'result' in mdjson.keys() else dict())
    print(mdlist.index(i),end='\r')
headers={
    'Host': 'www.bilibili.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Sec-Fetch-Dest': 'document',
    'Accept': 'text/html',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Referer': 'https://www.bilibili.com',
    'Accept-Encoding':'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie':cookie
}
tp_finished=re.compile(r'(\d+)年(\d+)月(\d+)日开播.*(\d+)')
tp_not_finished=re.compile(r'(\d+)年(\d+)月(\d+)日开播')
tp_movie=re.compile(r'(\d+)年(\d+)月(\d+)日上映')
def download():
    for i in new_mdlist:
        print(new_mdlist.index(i),end='\r')
        
        url='https://www.bilibili.com/bangumi/media/md'+str(i)
        
        try_time=0
        httperror=False
        while try_time<=5:
            try:
                r=ur.Request(url=url,headers=headers)
                response=opener.open(r) 
                break
            except ue.HTTPError as e:
                httperror=True
                print('Page Not found...skipped')
                break
            except Exception as e:
                try_time+=1
                print('retrying',try_time)
        else:
            raise Exception('Download Failed!!')
        
        if httperror:
            continue
        
        content=str(gzip.decompress(response.read()),'utf-8')
        response.close()
        
        soup=bs(content)
        tags=soup.find('div',class_='media-info-r').find_all('span',{'class':'media-tag'})
        tags=[each_tag.text for each_tag in tags]
        tags=' '.join(tags) if len(tags) else ''
        time=soup.find('div',class_='media-info-r').find_all('div',{'class':'media-info-time'})[0]
        
        res=re.search(tp_finished,time.text)
        finished=False
        if res is not None: # finished
            finished=True
            res=res.groups()
            date='-'.join(res[0:3])
            episodes=res[3]
        else:
            res=re.search(tp_not_finished,time.text)
            if res is not None: # not_finished
                res=res.groups()
                date='-'.join(res[0:3])
                episodes=0
            else:
                res=re.search(tp_movie,time.text)
                if res is not None: # a_movie
                    res=res.groups()
                    date='-'.join(res[0:3])
                    episodes=1
                else:
                    date=''
                    episodes=-1
        
        summary=summary_dict.get(str(i))
        
        dtesdict.update({str(i):{'tags':tags,'date':date,'episodes':episodes,'简介':summary if summary is not None else ''}})
        print(i,{'date':date,'episodes':episodes})
download()
bilidb2=[]
for i in range(len(bilidb)):
    a=dict()
    if not len(bilidb[i]):
        continue
    
    dtes=dtesdict.get(str(bilidb[i]['media']['media_id']))
    
    a.update({
            'title':bilidb[i]['media']['title'],
            'type_name':bilidb[i]['media']['type_name'],
            'season_id':bilidb[i]['media']['season_id'],
            'area':bilidb[i]['media']['areas'][0]['name'] if len(bilidb[i]['media']['areas'])>0 else '',
            'media_id':bilidb[i]['media']['media_id'],
            'rating':bilidb[i]['media']['rating']['score'] if 'rating' in bilidb[i]['media'].keys() else 0,
            'raters':bilidb[i]['media']['rating']['count'] if 'rating' in bilidb[i]['media'].keys() else 0,
            'cover':bilidb[i]['media']['cover'],
        
            'follow':bilidb[i]['follow'] if 'follow' in bilidb[i].keys() else 0,
            'series_follow':bilidb[i]['series_follow'] if 'series_follow' in bilidb[i].keys() else 0,
            'views':bilidb[i]['views'] if 'views' in bilidb[i].keys() else 0,
            'coins':bilidb[i]['coins'] if 'coins' in bilidb[i].keys() else 0,
            'danmakus':bilidb[i]['danmakus'] if 'danmakus' in bilidb[i].keys() else 0,
            'tags':dtes['tags'],
            'date':dtes['date'],
            'episodes':dtes['episodes'],
            '简介':dtes['简介']
             })
    bilidb2.append(a)

date=str(time.localtime().tm_mon)+'_'+str(time.localtime().tm_mday)
with open(r'bilibili\sslist_'+date+'.json','w') as fp:
    json.dump(list(ssurls),fp)
with open(r'bilibili\mdlist_'+date+'.json','w') as fp:
    json.dump(mdlist,fp)
with open(r'bilibili\bilidb_'+date+'.json','w') as fp:
    json.dump(bilidb2,fp)
with open(r'bilibili\dtesdict_'+date+'.json','w') as fp:
    json.dump(dtesdict,fp)
bilidb3=pd.DataFrame(bilidb2)
bilidb3.to_csv(r'bilibili\bilidb_'+date+'.csv',index=False)

headers={
    'Host': 'i0.hdslb.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Sec-Fetch-Dest': 'image',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'no-cors',
    'Referer': 'https://www.bilibili.com/bangumi/media/md1178/?from=search&seid=17806546061422186816',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
def select_data(month,day):
    return '_'+str(month)+'_'+str(day)
new_mdlist_series=pd.Series(new_mdlist,name='media_id')
new_covers=pd.merge(left=bilidb3,right=new_mdlist_series,on='media_id')[['media_id','cover']].copy()
def imgdl():
    for i in range(len(new_covers)):
        print(i,end='\r')
        url=new_covers.cover.values[i]
        md=new_covers.media_id.values[i]
        
        try_time=0
        httperror=False
        while try_time<=5:
            try:
                r=ur.Request(url=url,headers=headers)
                response=opener.open(r) 
                break
            except ue.HTTPError as e:
                httperror=True
                print('Page Not found...skipped')
                break
            except Exception as e:
                try_time+=1
                print('retrying',try_time)
        else:
            raise Exception('Download Failed!!')


        content=response.read()
        response.close()
        
        with open('bilibili\\covers\\' + str(md) + '.jpg','wb') as fp:
            fp.write(content)
imgdl()