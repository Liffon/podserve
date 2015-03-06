from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET
import urllib2
import pickle
import os
import functools

podcastsFilename = "podcasts.p"

if os.path.exists(podcastsFilename):
    podcasts = pickle.load(open(podcastsFilename, "rb"))
else:
    podcasts = dict()

def compose(*functions):
    def compose2(f, g):
        return lambda x: f(g(x))
    return functools.reduce(compose2, functions)

def wrap_in_tag(tag, inner):
    return "<" + tag + ">" + inner + "</" + tag + ">"

def make_link(text, url):
    return "<a href=\"" + url + "\">" + text + "</a>"

def fetch_title(url):
    raw_rss = urllib2.urlopen(url).read()
    xmlroot = ET.fromstring(raw_rss)
    return xmlroot[0].find("title").text

def show_episodes(self, (title, url), shortname=None):
    raw_rss = urllib2.urlopen(url).read()
    xmlroot = ET.fromstring(raw_rss)

    rssTitle = xmlroot[0].find("title").text
    if shortname: # update title if changed
        if title != rssTitle:
            podcasts[shortname] = (rssTitle, url)

    self.wfile.write(wrap_in_tag("h1", rssTitle))
    self.wfile.write(make_link("Back to index", "/"))
    self.wfile.write("<ul>")
    for item in reversed(xmlroot[0].findall('item')):
        self.wfile.write(
            wrap_in_tag("li",
                        make_link(item.find('title').text,
                                  item.find('enclosure').attrib['url']))
            .encode('utf8'))
    self.wfile.write("</ul>")

def show_add_form(self, name):
    self.wfile.write(wrap_in_tag("h1", "Add podcast"))
    self.wfile.write('<form action="/add!" method="get">')
    self.wfile.write('Shortname: ')
    self.wfile.write('<input type="text" name="name" value="%s" /><br />' % name)
    self.wfile.write('Url: ')
    self.wfile.write('<input type="text" name="url" /><br />')
    self.wfile.write('<input type="submit" value="Add" />')
    self.wfile.write('</form>')

class myHandler(BaseHTTPRequestHandler):
    def send_OK_header(self):
        self.send_response(200)
        self.send_header('Content-type','text/html; charset=utf-8')
        self.end_headers()

    def redirect(self, url):
        self.send_response(303)
        self.send_header('Location', url)
        self.end_headers()

    def do_GET(self):
        if '?' in self.path:
            self.path, self.query_string = self.path.split('?', 1)
        else:
            self.query_string = ''

        request = self.path[1:]

        if self.path == '/stop!':
            print "Stopping!"
            self.server.socket.close()

        elif request in podcasts: # if known podcast
            self.send_OK_header()
            show_episodes(self, podcasts[request], request)

        elif self.path == '/': # index
            self.send_OK_header()

            self.wfile.write(wrap_in_tag("h1", "Podcasts"))
            self.wfile.write("<ul>")
            for shortname, (title, url) in podcasts.iteritems():
                self.wfile.write(
                    wrap_in_tag("li",
                                make_link(title, '/' + shortname)))
            self.wfile.write("</ul>")
            self.wfile.write(make_link("Add another", "/add!"))
            self.wfile.write("<br />")
            self.wfile.write(make_link("Remove one", "/remove!"))

        elif self.path == '/add!':
            def maybeSplitOn(splitter):
                def f(str):
                    if splitter in str:
                        return str.split(splitter)
                    else:
                        return str
                return f

            parameters = {}
            if len(self.query_string) != 0:
                tuples = map(compose(tuple,
                                     maybeSplitOn('=')),
                             maybeSplitOn('&')(self.query_string))
                print tuples
                parameters = dict(tuples)

            if parameters.get('name', False) and parameters.get('url', False):
                shortname = parameters['name']
                url = urllib2.unquote(parameters['url'])
                title = fetch_title(url)
                podcasts[shortname] = (title, url)

                pickle.dump(podcasts, open(podcastsFilename, "wb"))

                self.redirect("/")
            else:
                show_add_form(self, '')

        elif self.path == '/remove!':
            if len(self.query_string) == 0:
                self.send_OK_header()
                self.wfile.write(wrap_in_tag("h1", "Remove podcast"))
                self.wfile.write('<ul style="background-color: red">')
                for shortname, (title, url) in podcasts.iteritems():
                    self.wfile.write(
                        wrap_in_tag("li",
                                    make_link(title, '/remove!?' + shortname)))
                self.wfile.write("</ul>")
                self.wfile.write(make_link("Back to index", "/"))
            else:
                shortname = self.query_string
                if shortname in podcasts:
                    podcasts.pop(shortname)
                self.redirect("/remove!")

        else: # No known podcast
            self.send_OK_header()
            show_add_form(self, request)

try:
    server = HTTPServer(('', 8000), myHandler)
    server.serve_forever()

except KeyboardInterrupt:
    server.socket.close()
