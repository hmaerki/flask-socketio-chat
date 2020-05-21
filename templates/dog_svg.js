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
// TODO(Peter): Values
snap.attr({ viewBox: "-130 -130 260 260" });

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

for (var i = 0; i < {{ game.dgc.PLAYER_COUNT }}; i++) {
  for (var c = 0; c < 6; c++) { 
    id = i*{{ game.dgc.PLAYER_COUNT }}+c+'card'
    textCard = groupBoard.text(0, 60, 'Card ' + id)
    textCard.attr({
      fontSize: '6px'
    });
    textCard.node.id = id
    // var angle = i*360.0/{{game.dgc.PLAYER_COUNT}}
    // textCard.animate({ transform: 'r' + angle + ',0,0' }, 5000, mina.bounce );
    // textCard.click(card_click)
  }
}

var name_click = function() {
  name = window.prompt("Name:", "...");
  if (name) {
    var msg = { event: 'newName', idx: parseInt(this.node.id), name: name};
    DogApp.socket.emit("event", msg);
  }
}

for (var i = 0; i < {{ game.dgc.PLAYER_COUNT }}; i++) { 
  textPlayer = groupBoard.text(0,70, 'Player ' + i)
  textPlayer.attr({
    fontSize: '10px',
    "text-anchor": "middle"
  });
  textPlayer.node.id = i+'name'
  var angle = i*360.0/{{game.dgc.PLAYER_COUNT}}
  textPlayer.animate({ transform: 'r' + angle + ',0,0' }, 5000, mina.bounce );
  textPlayer.click(name_click)
}

var button_click = function() {
  var label = this.node.textContent
  if (label === 'R') {
    DogApp.playerIndex = (1+DogApp.playerIndex) % {{game.dgc.PLAYER_COUNT}}
    var angle = DogApp.playerIndex*360.0/{{game.dgc.PLAYER_COUNT}}
    groupBoard.animate({ transform: 'r' + angle + ',0,0' }, 3000, mina.bounce );
    return;
  }

  var msg = { event: 'buttonPressed', label: label};
  DogApp.socket.emit("event", msg);

  if (label.startsWith('G')) {
    window.location.reload(false);
  }
}

const buttons = ["G2", "G4", "G6", "C", "R", "2", "3", "4", "5", "6"]
buttons.forEach(function (text, i) {
  textButton = snap.text(-120,90-i*12, text)
  textButton.attr({
    fontSize: '10px',
    "text-anchor": "middle",
    class: 'button'
  });
  textButton.node.id = i+'button'
  textButton.click(button_click)
});

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

