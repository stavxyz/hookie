hookie
===================

wraps a few of github's v3 API webhooks calls

#### install & use
```
$ pip install https://github.com/smlstvnh/hookie/archive/master.zip
$ hookie run --create http://jenkins.hookie.net:8080/ghprbhook/ -u smlstvnh -r hookie
Creating hook [ http://jenkins.hookie.net:8080/ghprbhook/ ] for smlstvnh -- hookie
```

#### or use with an enterprise github
set up your [`hookie/hookie.yaml`](https://github.com/smlstvnh/hookie/blob/master/hookie/hookie.yaml)
  * otherwise, defaults to https://api.github.com

see existing hooks and their parameters
```
$ hookie show -u smlstvnh -r hookie
```

------------

#### sample workflow

```
$ hookie show -u smlstvnh -r hookie
------------------------------------
 ### WEBHOOKS ON smlstvnh:hookie ###
------------------------------------
```
Nothing yet. Let me create one. 
```
$ hookie run --create http://jenkins.hookie.net:8080/ghprbhook/ -u smlstvnh -r hookie
fetching list of existing hooks for smlstvnh:hookie

Creating hook [ http://jenkins.hookie.net:8080/ghprbhook/ ] for smlstvnh -- hookie
```
Show the details. 
```
$ hookie show -u smlstvnh -r hookie
------------------------------------
 ### WEBHOOKS ON smlstvnh:hookie ###
------------------------------------
--- ID: 1745140 ---
{u'active': True,
 u'config': {u'content_type': u'form',
             u'insecure_ssl': u'1',
             u'url': u'http://jenkins.hookie.net:8080/ghprbhook/'},
 u'created_at': u'2014-01-30T00:27:09Z',
 u'events': [u'issue_comment', u'pull_request'],
 u'id': 1745140,
 u'last_response': {u'code': None, u'message': None, u'status': u'unused'},
 u'name': u'web',
 u'test_url': u'https://api.github.com/repos/smlstvnh/hookie/hooks/1745140/test',
 u'updated_at': u'2014-01-30T00:27:09Z',
 u'url': u'https://api.github.com/repos/smlstvnh/hookie/hooks/1745140'}
------------------------------------
```

------
NOTE:  

* hookie is currently set up (because I primarily use it with [ghprb](https://github.com/janinko/ghprb)) so that webhooks it creates will trigger on
  * `events: ['issue_comment', 'pull_request']`
* I will make that, and more of these parameters dynamic as soon as it's needed. 

-----


Time for a deletion.

```
$ hookie run --delete bogus -u smlstvnh -r hookie
fetching list of existing hooks for smlstvnh:hookie

! That doesn't look like a webhook id.

No hooks found to delete. Tried to delete [ bogus ]
Try deleting one of:
  > id: [1745140] -- url: [http://jenkins.hookie.net:8080/ghprbhook/]
```

Right.

```
$ hookie run --delete 1745140 -u smlstvnh -r hookie
fetching list of existing hooks for smlstvnh:hookie

Deleting hook with id => 1745140 from smlstvnh:hookie
<Response [204]>
```


