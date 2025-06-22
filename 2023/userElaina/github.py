_debug=True
_muti=False

import os
import json
import random
import requests
from urllib.parse import quote_from_bytes

def bencode(x:all)->bytes:
	if isinstance(x,(bytes,bytearray,memoryview,)):
		x=bytes(x)
	else:
		x=str(x).encode(encoding='utf8')
	return x

def urlencode(s:all)->str:
	return quote_from_bytes(bencode(s))

def rd(l):
	return random.choice(list(l))

pool=set()
pool_noconnect=set()
pool_limit=set()
_port=-1
def gt(u):
	
	if not _muti:
		global _port
	else:
		_port=rd(pool)

	flg=True
	while flg:
		proxies={'http':'http://127.0.0.1:'+str(_port),'https':'http://127.0.0.1:'+str(_port)}
		try:
			res=requests.get(u,proxies=proxies).content
			if b'https://docs.github.com/rest/overview/resources-in-the-rest-api' in res:
				print('ERROR:rate limit (port',_port)
				if _debug:
					_port=input('new port: ')
				else:
					pool.discard(_port)
					pool_limit.add(_port)
					_port=rd(pool)
			else:
				flg=False
		except:
			print('ERROR: noconnection (port',_port)
			if _debug:
				_port=input('new port: ')
			else:
				pool.discard(_port)
				pool_noconnect.add(_port)
				_port=rd(pool)
	return res

false=False
true=True
null='None'

def creep_repo(name:str='userElaina')->tuple:
	l_u=list()
	l_archive=list()
	l_fork=list()

	u='https://api.github.com/users/'+name+'/repos?sort=updated&pre_page=100&page='
	for page in range(1,2333):
		res=gt(u+str(page))
		l=eval(res.decode('utf8'))
		if not l:
			break
		for i in l:
			s='['+i['name']+']('+i['html_url']+'): '+i['description']
			if i['fork']:
				l_fork.append(s)
			elif i['archived']:
				l_archive.append(s)
			else:
				l_u.append(s)

	p=os.path.join(os.getcwd(),name+'-repo.md')
	open(p,'wb')

	l=['## My Repositorys',]
	l+=['### To Do',]+l_u
	l+=['### Archived',]+l_archive
	l+=['### Fork',]+l_fork

	for i in l:
		open(p,'ab').write(i.encode('utf8')+b'\n\n')

	return len(l_u),len(l_archive),len(l_fork),

def creep_star(name:str='userElaina')->tuple:
	l_star=list()

	u='https://api.github.com/users/'+name+'/starred?sort=updated&pre_page=100&page='
	for page in range(1,2333):
		res=gt(u+str(page))
		l=eval(res.decode('utf8'))
		if not l:
			break
		for i in l:
			s='['+i['full_name']+']('+i['html_url']+'): '+i['description']
			l_star.append(s)
	
	p=os.path.join(os.getcwd(),name+'-star.md')
	open(p,'wb')

	for i in ['## Starred Repositorys',]+l_star:
		open(p,'ab').write(i.encode('utf8')+b'\n\n')

	return len(l_star),

def creep_follow(name:str='userElaina')->tuple:
	l_follow=list()

	u='https://api.github.com/users/'+name+'/following?sort=updated&pre_page=100&page='
	for page in range(1,2333):
		res=gt(u+str(page))
		l=eval(res.decode('utf8'))
		if not l:
			break
		for i in l:
			res=gt(i['url'])
			i=json.loads(res)
			for j in ['name','login','bio','blog','company','location','twitter_username','email']:
				if j in i:
					if i[j] in (None,'None',0,False,'False'):
						i[j]=None
				else:
					i[j]=None
			l_user=list()
			un=i['login']
			l_user.append('### [![head](https://avatars.githubusercontent.com/'+un+'?v=4&s=32)]('+i['html_url']+') '+str(i['name'])+' ('+un+')')
			l_user.append('')
			if i['bio']:
				l_user.append(i['bio'])
				l_user.append('')

			if i['blog']:
				if not i['blog'].startswith('http'):
					i['blog']='https://'+i['blog']
				l_user.append('blog: '+i['blog']+'   ')
			if i['company']:
				l_user.append('company: '+i['company']+'   ')
			if i['blog'] or i['company']:
				l_user.append('')

			if i['location']:
				_enc=urlencode(i['location'])
				l_user.append('[![](https://img.shields.io/badge/Location-'+_enc+'-4285f4?style=flat-square&logo=google-maps)](https://www.google.com/maps/place/'+_enc+')   ')
			if i['twitter_username']:
				l_user.append('[![](https://img.shields.io/badge/Twitter-'+i['twitter_username']+'-1da1f2?style=flat-square&logo=twitter)](https://twitter.com/'+i['twitter_username']+')   ')
			if i['location'] or i['twitter_username']:
				l_user.append('')

			if i['email']:
				_x,_y=i['email'].lower().split('@')
				if _y in ('protonmail.com','pm.me'):
					w=('ProtonMail',_x,'8b89cc','protonmail','https://pm.me/')
				elif _y=='gmail.com':
					w=('Gmail',_x,'ea4335','gmail','https://gmail.com/')
				else:
					w=(_y,_x,'005ff9','mail.ru','https://gmail.com/')
				l_user.append('[![](https://img.shields.io/badge/%s-%s-%s?style=flat-square&logo=%s)](%s)    '%w)
				l_user.append(i['email'])
				l_user.append('')

			l_follow.append(l_user)

	p=os.path.join(os.getcwd(),name+'-follow.md')
	open(p,'wb')

	for i in l_follow:
		for j in i:
			open(p,'ab').write(j.encode('utf8')+b'\n')

	return len(l_follow),

pool={23301+(i<<1) for i in range(10)}
_port=rd(pool)
print(creep_repo())
print(creep_star())
print(creep_follow())
