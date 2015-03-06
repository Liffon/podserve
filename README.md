Intro
=====

A small script to download podcast episodes via a web interface. Tested on Python 2.7.2.

I made it for my old Nokia phone that doesn't have a podcast client, and only a primitive browser. I can download mp3 files and play them on the phone, but web pages are hard to navigate so I needed something simple to keep links to my podcast episodes in one place.

I use it by starting the script on a computer when I need to download a new podcast episode, then going to http://<server-ip>:8000/ in the phone's browser.

Usage
=====

Run the script with `python podserve.py` to start a server on port 8000.

Point a browser to, if on local machine, [http://localhost:8000/](http://localhost:8000/) to get an empty list of podcasts. Add new podcasts with the link at the bottom.

To get a list of episodes, select a link on the index page. Then just select one of the links to download the corresponding episode.

All podcasts are saved and reloaded the next time you run the script. To clear the list of podcasts, delete podcasts.p in the folder you ran the script.
