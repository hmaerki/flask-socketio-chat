// http://snapsvg.io/docs/
// http://snapsvg.io/demos/
// http://snapsvg.io/start/
// http://svg.dabbles.info/snaptut-responsive
// https://wiki.selfhtml.org/wiki/SVG/Tutorials/Einstieg/SVG_in_responsiven_Webseiten
// https://css-tricks.com/scale-svg/

// First lets create our drawing surface out of existing SVG element
// If you want to create new surface just provide dimensions
// like snap = Snap(800, 600);
// var snap = Snap("#svg");
var snap = Snap("#svg");
snap.attr({ viewBox: "-100 -100 200 200" });

groupBoard = snap.g()

// var lineTopdiag = groupBoard.line(-90, -90, 90, 90)
// lineTopdiag.attr({
//   stroke: "#000",
//   strokeWidth: 1
// })

var circleMask = groupBoard.circle(0, 0, 100).attr({ fill: 'white' });
var board = groupBoard.image("static/board{{ game.dbc.BOARD_ID }}/board.jpg", -100, -100, 200, 200);
board.attr({
  class: "board",
  mask: circleMask
})

var name_click = function() {
  name = window.prompt("Name:", "...");
  // TODO: Send name to server
  var msg = { event: 'newName', idx: parseInt(this.node.id), name: name};
  DogApp.socket.emit("event", msg);
}


for (var i = 0; i < {{ game.dgc.PLAYER_COUNT }}; i++) { 
  textPlayer = groupBoard.text(0,70, 'Player ' + i)
  textPlayer.attr({
    fontSize: '10px',
    opacity: 1.0,
    "text-anchor": "middle"
  });
  textPlayer.node.id = i+'name'
  var angle = i*360.0/{{game.dgc.PLAYER_COUNT}}
  textPlayer.animate({ transform: 'r' + angle + ',0,0' }, 5000, mina.bounce );
  textPlayer.click(name_click)
}


// var angle = DogApp.playerIndex * 360 / DogApp.playerCount
// groupBoard.animate({ transform: 'r' + angle + ',0,0' }, 2000, mina.bounce );
// groupBoard.attr({transform: 'r' + angle + ',0,0'});


//
// Moving the cicle will emit messages to the server
//
var move = function (dx, dy, mouseX, mouseY) {

  m = groupBoard.node.transform.baseVal[0].matrix
  // console.log('groupBoard.node.transform.baseVal[0].matrix.: ' + m.a + ', ' + m.b + ', ' + m.c + ', ' + m.d + ', ' + m.e + ', ' + m.f)

  dx2 = + m.a*dx - m.c*dy;
  dy2 = - m.b*dx + m.d*dy;

  m = snap.transform().globalMatrix;
  factor = m.a;
  dx2 /= factor;
  dy2 /= factor;
  cx = DogApp.start_cx + dx2;
  cy = DogApp.start_cy + dy2;
  // this.attr({ cx: cx, cy: cy });

  // DogApp.socket.emit("move", {id: this.id, cx: this.node.getAttribute("cx"), dx: dx});
  // var move_msg = { id: this.node.id, cx: cx|0, cy: cy|0 }
  // var move_msg = { id: this.node.id, x: cx|0, y: cy|0 }
  var move_msg = {
    'svg_id': '#' + this.node.id,
    'marble': [cx|0, cy|0]
  }
  DogApp.socket.emit("marble", move_msg);
}

var start = function () {
  // DogApp.start_cx = this.node.cx.baseVal.value;
  // DogApp.start_cy = this.node.cy.baseVal.value;
  DogApp.start_cx = this.node.x.baseVal.value;
  DogApp.start_cy = this.node.y.baseVal.value;
}

var stop = function () {
  console.log('finished dragging');
}

for (i=0; i<4*DogApp.playerCount; i++) {
  var circleMarble = groupBoard.image("static/img/" + DogApp.playerCount + "/marble" + (10+i) + ".png", 0, 0, 8, 8);
  circleMarble.attr({
    class: "marble",
    x: 2*i,
    y: 1*i
  });
  circleMarble.node.id="marble"+i
  circleMarble.drag(move, start, stop)
}

