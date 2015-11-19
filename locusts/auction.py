from locust import HttpLocust, TaskSet, task
from pyquery import PyQuery
import json
import tinycss
from tinycss.font3 import CSSFontfaceParser


class AuctionTest(TaskSet):
    tender_id = None
    tender_src = None
    last_change = 0
    csses = []

    def on_start(self):
        self.reload_last_tender()

    def index(self):
        resp = self.client.get("/")
        if resp.status_code == 200:

            pq = PyQuery(resp.content)
            a_first = pq('.list-group-item:first a')
            if a_first:
                tender_url = a_first[0].get('href')
                self.tender_id = tender_url.split('/')[-1]


    def tender(self):
        resp = self.client.get('/tenders/{0}'.format(self.tender_id))
        if resp.status_code == 200:
            self.tender_src = resp.content

    @task(1)
    def reload_last_tender(self):
        self.index()
        self.tender()

    @task(10)
    def css(self):
        pq = PyQuery(self.tender_src)

        for style in pq('link[rel="stylesheet"]'):
            href = style.get('href')
            if href and href.startswith('/'):
                resp = self.client.get(href)
                if resp.status_code == 200:
                    css = resp.content
                    self.csses.extend(tinycss.make_parser(CSSFontfaceParser).parse_stylesheet(unicode(css)).rules)

    @task(10)
    def images(self):

        for rules in self.csses:
            if rules.at_keyword is None:
                decs = rules.declarations
                for dec in decs:
                    tokens = dec.value
                    for token in tokens:
                        if token.type == 'URI':

                            uri = token.value

                            uri = uri.replace('../../', '/')
                            uri = uri.replace('../', '/min/')

                            if uri.startswith('/'):
                                self.client.get(uri)

    @task(100)
    def fonts(self):
        print "inside fonts"

        for rules in self.csses:
            print rules
            if rules.at_keyword == '@font-face':
                tokens = rules.body
                for token in tokens:
                    if token.type == 'URI':

                        uri = token.value

                        uri = uri.replace('../../', '/')
                        uri = uri.replace('../', '/static/')

                        if uri.startswith('/'):
                            print "getting " + uri
                            self.client.get(uri)

    @task(10)
    def js(self):
        pq = PyQuery(self.tender_src)

        for script in pq('script'):
            src = script.get('src')
            if src and src.startswith('/'):
                self.client.get(src)

    @task(20)
    def time(self):
        self.client.get('/get_current_server_time')

    @task(10)
    def auctions(self):
        self.client.get('/auctions/')
        self.client.get('/auctions/{0}'.format(self.tender_id))

    @task(30)
    def changes(self):
        params = {
            'timeout': 25000,
            'style': 'main_only',
            'include_docs': 'true',
            'feed': 'longpoll',
            'filter': '_doc_ids',
            'since': self.last_change,
            'limit': 25,
            'doc_ids': '["{0}"]'.format(self.tender_id)
        }
        resp = self.client.get('/auctions/_changes', params=params)
        if resp.status_code == 200:
            self.last_change = json.loads(resp.content)['last_seq']


class AuctionUser(HttpLocust):
    host = "https://auction-sandbox.openprocurement.org"
    min_wait = 0
    max_wait = 0
    task_set = AuctionTest
