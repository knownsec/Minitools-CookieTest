#!/usr/bin/env python
#coding:utf-8
import optparse
import urlparse
import requests
import copy

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13C75 MicroMessenger/6.3.8 NetType/WIFI Language/zh_CN"

def paramToDict(ptype, value):
    retVal = {}
    if not value:
        return retVal        

    splitChar = ';' if ptype.lower() == 'cookie' else '&'

    try:
        splitParams = value.split(splitChar)
        for element in splitParams:
            elem = element.split("=")
            if len(elem) >= 2:
                parameter = elem[0].replace(" ", "")
                value = "=".join(elem[1:])  # a.php?id=1&id=2&id=3
                retVal[parameter] = value
    except Exception, e:
        print '%s' % e
    return retVal

def dictToParam(value, isget=False):
    """{'a':1,'b':2} to a=1; b=2"""
    if isget:
        params = '&'.join(['%s=%s' % (k, v) for k, v in value.items() if k is not None])
    else:
        params = ';'.join(['%s=%s' % (k, v) for k, v in value.items() if k is not None])
    return params

def testLogin(url, keyword=None, data=None, cookies=None, useragent=None, referer=None):
    retVal = False
    
    headers = {
        'user-agent': useragent or UA,
        'referer': referer or url
    }

    cookiesDict = paramToDict('cookie', cookies)
    if data is not None:
        if isinstance(data, basestring):
            data = paramToDict('post', data)
        r = requests.post(url, data=data, cookies=cookiesDict, headers=headers)
    else:
        r = requests.get(url, cookies=cookiesDict, headers=headers)
    retVal = 'ok' if keyword and keyword in r.content else r.content
    
    return retVal
    
def getTest(url, keyword, data=None, cookies=None, useragent=None, referer=None):
    retVal = {}
    headers = {
        'user-agent': useragent or UA,
        'referer': referer or url
    }
    o = urlparse.urlparse(url)
    if not o.query:
        return retVal
    else:
        getDict = paramToDict('get', o.query)
        cookiesDict = paramToDict('cookie', cookies)
        delGet = None
        testGet = copy.deepcopy(getDict)
        for item in getDict:
            print "[*] Testing GET param '%s'" %item
            if testGet.has_key(delGet):
                del testGet[delGet]

            tests = copy.deepcopy(testGet)
            del tests[item]

            url ="%s://%s%s" %(o.scheme, o.netloc, o.path)
            r = requests.get(url, params=tests, cookies=cookiesDict)
            if keyword not in r.content:
                retVal[item] = getDict[item]
                print "[*] Found keyword GET param: '%s=%s'" %(item, getDict[item])
            else:
                delGet = item

    return retVal

def postTest(url, keyword, data=None, cookies=None, useragent=None, referer=None):
    retVal = {}
    headers = {
        'user-agent': useragent or UA,
        'referer': referer or url
    }
    if data is None:
        print "[*] No postdata."
        return retVal
    else:
        postDict = paramToDict('post', data)
        cookiesDict = paramToDict('cookie', cookies)
        delPost = None
        testPost = copy.deepcopy(postDict)
        for item in postDict:
            print "[*] Testing POST param '%s'" %item
            if testPost.has_key(delPost):
                del testPost[delPost]

            tests = copy.deepcopy(testPost)
            del tests[item]

            r = requests.post(url, data=tests, cookies=cookiesDict)
            if keyword not in r.content:
                retVal[item] = postDict[item]
                print "[*] Found keyword POST param: '%s=%s'" %(item, postDict[item])
            else:
                delPost = item

    return retVal

def cookieTest(url, keyword, data=None, cookies=None, useragent=None, referer=None):

    retVal = {}
    headers = {
        'user-agent': useragent or UA,
        'referer': referer or url
    }

    cookiesDict = paramToDict('cookie', cookies)
    delCookie = None
    testCookies = copy.deepcopy(cookiesDict)

    for item in cookiesDict:
        print "[*] Testing cookie '%s'" %item
        if testCookies.has_key(delCookie):
            del testCookies[delCookie]
            
        tests = copy.deepcopy(testCookies)
        
        del tests[item]

        if data is not None:
            if isinstance(data, basestring):
                data = paramToDict('post', data)
            r = requests.post(url,data=data, cookies=tests, headers=headers)
        else:
            r = requests.get(url, cookies=tests, headers=headers)

        if keyword not in r.content:
            retVal[item] = cookiesDict[item]
            print "[*] Found cookie: '%s=%s' is a session cookie" %(item, cookiesDict[item])
        else:
            delCookie = item

    return retVal

def main():
    parser = optparse.OptionParser(version='0.1')
    parser.add_option("-u", "--url", dest="url", help="Target URL (e.g. \"http://www.target.com/page.php?id=1\")")
    parser.add_option("--data", dest="data", help="POST data (e.g. \"query=test\")")
    parser.add_option("--cookie", dest="cookie", help="HTTP Cookie header value")
    parser.add_option("--user-agent", dest="ua", help="HTTP User-Agent header value")
    parser.add_option("--referer", dest="referer", help="HTTP Referer header value")
    parser.add_option("-k", "--keyword", dest="keyword", help="Cookie login success keyword")
    options, _ = parser.parse_args()
    if options.url and options.cookie:
        test = testLogin(options.url if options.url.startswith("http") else "http://%s" % options.url, options.keyword, data=options.data, cookies=options.cookie, useragent=options.ua, referer=options.referer)
        if test == 'ok':
            msg = "[*] Cookies login with keyword '%s'" %options.keyword
            print msg
        else:
            print test
            msg = "[!] Cookies is not login! you should retry with another cookies again."
            print msg
            return
            
        result = cookieTest(options.url if options.url.startswith("http") else "http://%s" % options.url, options.keyword, data=options.data, cookies=options.cookie, useragent=options.ua, referer=options.referer)
        print "\n[*] Cookie test result: %s\n" %dictToParam(result)
        result = getTest(options.url if options.url.startswith("http") else "http://%s" % options.url, options.keyword, data=options.data, cookies=options.cookie, useragent=options.ua, referer=options.referer)
        print "\n[*] Get test result: %s\n" %dictToParam(result, isget=True)
        if options.data is not None:
            result = postTest(options.url if options.url.startswith("http") else "http://%s" % options.url, options.keyword, data=options.data, cookies=options.cookie, useragent=options.ua, referer=options.referer)
            print "\n[*] Post test result: %s\n" %dictToParam(result, isget=True)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()