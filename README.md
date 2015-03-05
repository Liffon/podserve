Intro
=====

A small script to access podcast links via a web interface. Tested on Python 2.7.2.

I made it for my old Nokia phone that doesn't have a podcast client, and only a primitive browser. I can download mp3 files and play them on the phone, but web pages are hard to navigate so I needed something simple to keep links to my podcast episodes in one place.

I use it by starting the script on a computer when I need to download a new podcast episode, then going to http://computer:8000/ in the phone's browser.

Usage
=====

Run the script with `python podserve.py` to start a server on port 8000.

Point a browser to, if on local machine, http://localhost:8000/ to get an empty list of podcasts.

Add a new podcast by visiting http://localhost:8000/name-of-podcast/ and you will be provided a page where you can paste a link to a podcast formatted rss feed. It is then added to the front page at http://localhost:8000/.

The next time you visit http://localhost:8000/name-of-podcast/, links to all episodes of name-of-podcast will be shown. Add more podcasts by visiting http://localhost:8000/name-of-other-podcast/.

All podcasts are saved and reloaded the next time you run the script. To clear the list of podcasts, delete podcasts.p in the folder you ran the script.
