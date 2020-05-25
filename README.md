## Snap documentation
* http://snapsvg.io/docs/
* http://snapsvg.io/demos/
* http://snapsvg.io/start/
* http://svg.dabbles.info/snaptut-responsive
* https://wiki.selfhtml.org/wiki/SVG/Tutorials/Einstieg/SVG_in_responsiven_Webseiten
* https://css-tricks.com/scale-svg/
* http://filamentgroup.github.io/layersnap/demo/

## TODO

 * Mousepointer

http://dogspiel.ch:5000/4/test1
 6 Karten verteilen
 einmal rotieren
 jetzt sind die Hilfstexte links statt unten

http://dogspiel.ch:5000/4/test
 habe Karten verteilt, immer wieder und bereits verteilt als die Karten noch geflogen sind. Jetzt kann ich keine Karten mehr veteilen.

Ich habe noch teils Kugeln etwas aufgehellt. 

## Original text
This code goes along with this video: https://youtu.be/RdSrkkrj3l4

It covers a simple SocketIO app in Flask.

# how to build with docker
docker container rm --force dog_container
docker build -t dog .
docker run --rm -it -p 5000:5000 --name dog_container dog
