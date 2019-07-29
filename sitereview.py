# -*- coding: utf-8 -*-
import requests
import time

class SiteReview( object ):

    def __init__( self, interval = 8, proxies = None ):
        self.session = requests.Session()
        self.lookup = 'https://sitereview.bluecoat.com/resource/lookup'
        self.submit = 'https://sitereview.bluecoat.com/resource/submitCategorization'
        self.captcha = 'https://sitereview.bluecoat.com/resource/captcha-request'
        self.interval = interval
        self.lastoutput = None
        self.headers = {
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'accept-language' : 'en',
                        'Connection' : 'keep-alive',
                        'Content-Type': 'application/json; charset=UTF-8',
                        'Host' : 'sitereview.bluecoat.com',
                        'Origin' : 'https://sitereview.bluecoat.com',
                        'Referer' : 'https://sitereview.bluecoat.com',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
        self.proxies = proxies
        self._retrieve_xsrf_token()
    
    def _retrieve_xsrf_token( self ):
        payload = {"check":"captcha"}
        r = self.session.post( self.captcha, headers = self.headers, json = payload, proxies = self.proxies )
        cookie = r.request.headers[ 'Cookie' ]
        xsrf = cookie[ len( 'xsrf-token' ) + 1 : ]
        setcookie = r.headers[ 'Set-Cookie' ]
        jsessionid = setcookie[ : setcookie.index( ';' ) ]
        self.headers[ 'X-XSRF-TOKEN' ] = xsrf
        self.headers[ 'Cookie' ] = f'XSRF-TOKEN={xsrf}; {jsessionid}'
        
    def url_lookup( self, url ):
        payload = { "url": url, "captcha": "" }
        try:
            r = self.session.post( self.lookup, json = payload, headers = self.headers, proxies = self.proxies )
            j = r.json()
            categorization = []
            for el in j[ 'categorization' ]:
                categorization.append( el[ 'name' ] )
            return categorization
        except ConnectionError as e:
            print( 'Connection Error:', e )
        except Exception as e:
            print( "Exception:", e )
        
    def bulk_lookup( self, urls ):
        self.ioc = []
        self.badurls = []
        count = 1

        for url in urls[ :-1 ]:
            print (f"{count}. " )
            item = { "url": url, "categorization": self.url_lookup( url ) }
            self.ioc.append( item )
            print( item )
            time.sleep( self.interval )
            count += 1
        
        print (f"{count}. " )
        item = { "url": urls[ -1 ], "categorization": self.url_lookup( urls[ -1 ] ) }
        self.ioc.append( item )
        print( item )
        return self.ioc

if __name__ == "__main__":
    s = SiteReview()
    urls = s.bulk_lookup( [ "http://www.fivestoreyprojects.com/hjcf?fslt=37878", "http://www.rebelknife.com/bslj?yuvc=12534" ] )