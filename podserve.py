from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET
import urllib2
import pickle
import os

podcastsFilename = "podcasts.p"

if os.path.exists(podcastsFilename):
    podcasts = pickle.load(open(podcastsFilename, "rb"))
else:
    podcasts = dict()

globalKeepRunning = True
def keep_running():
    return globalKeepRunning

def wrap_in_tag(tag, inner):
    return "<" + tag + ">" + inner + "</" + tag + ">"

def make_link(text, url):
    return "<a href=\"" + url + "\">" + text + "</a>"

def show_episodes(self, url):
    raw_rss = urllib2.urlopen(url).read()
    xmlroot = ET.fromstring(raw_rss)

    self.wfile.write(wrap_in_tag("h1", xmlroot[0].find("title").text))
    self.wfile.write("<ul>")
    for item in reversed(xmlroot[0].findall('item')):
        self.wfile.write(
            wrap_in_tag("li",
                        make_link(item.find('title').text,
                                  item.find('enclosure').attrib['url']))
            .encode('utf8'))
    self.wfile.write("</ul>")

class myHandler(BaseHTTPRequestHandler):
    def send_OK_header(self):
        self.send_response(200)
        self.send_header('Content-type','text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        if self.path.find('?') != -1:
            self.path, self.query_string = self.path.split('?', 1)
        if self.path == '/stop!':
            print "Stopping!"
            self.server.socket.close()

        elif podcasts.get(self.path[1:], False):
            self.send_OK_header()
            show_episodes(self, podcasts[self.path[1:]])

        elif self.path == '/': # index
            self.send_OK_header()

            self.wfile.write(wrap_in_tag("h1", "Podcasts"))
            self.wfile.write("<ul>")
            for podcast in podcasts:
                self.wfile.write(wrap_in_tag("li",
                                             make_link(podcast, '/' + podcast)))
            self.wfile.write("</ul>")
        elif self.path == '/add!':
            def splitOnEquals(lst): return lst.split('=')
            parameters = map(splitOnEquals, self.query_string.split('&'))
            parameters = dict(map(tuple, parameters))

            if parameters.get('name', False) and parameters.get('url', False):
                name = parameters['name']
                url = urllib2.unquote(parameters['url'])
                podcasts[name] = url

                pickle.dump(podcasts, open(podcastsFilename, "wb"))

                self.send_OK_header()
                self.wfile.write("Added this podcast:")
                show_episodes(self, url)
        else: # No known podcast
            self.wfile.write(wrap_in_tag("h1", "Add podcast"))
            self.wfile.write('<form action="/add!" method="get">')
            self.wfile.write('Name: ')
            self.wfile.write('<input type="text" name="name" value="' +
                             self.path[1:] + '" /><br />')
            self.wfile.write('Url: ')
            self.wfile.write('<input type="text" name="url" /><br />')
            self.wfile.write('<input type="submit" value="Add" />')

try:
    server = HTTPServer(('', 8000), myHandler)
    server.serve_forever()

except KeyboardInterrupt:
    server.socket.close()
