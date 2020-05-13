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

var lineTopdiag = groupBoard.line(-90, -90, 90, 90)
lineTopdiag.attr({
  stroke: "#000",
  strokeWidth: 5
})


var board = groupBoard.image("static/img/20030731_181107_dog_4.jpg", -90, -90, 180, 180);
board.attr({
// x: 10,
// y: 10,
// width: 200,
// height: 200,
opacity: 0.2,
class: "draggable"
})

groupBoard.animate({ transform: 'r90,0,0' }, 2000, mina.bounce );


var rectBorder = groupBoard.rect(-50, -50, 100, 100, 10, 10)
rectBorder.attr({
  // fill: "#888",
  fill: "#f00",
  stroke: "#000",
  strokeWidth: 1,
  opacity: 0.5,
})


//   // transform = circleDraggableGreen.transform().local + (circleDraggableGreen.transform().local ? "T" : "t") + [dx, dy]
//   console.log("transform: " + transform)
//   circleColorChange.attr({
//     transform: transform
//   });
//   board.animate({ transform: transform}, 100)
// }

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
  this.attr({ cx: cx, cy: cy });

  // DogApp.socket.emit("move", {id: this.id, cx: this.node.getAttribute("cx"), dx: dx});
  var move_msg = { id: this.node.id, cx: cx|0, cy: cy|0 }
  DogApp.socket.emit("move", move_msg);
}

var start = function () {
  DogApp.start_cx = this.node.cx.baseVal.value;
  DogApp.start_cy = this.node.cy.baseVal.value;
}

var stop = function () {
  console.log('finished dragging');
}

for (c=0; c<2; c++) {
  for (i=0; i<2; i++) {
    var circleDraggableGreen = groupBoard.circle(0, 0, 50);
    // By default its black, lets change its attributes
    circleDraggableGreen.attr({
      // fill: "#bada55",
      stroke: "#000",
      strokeWidth: 2,
      class: "marble_"+c,
    });
    circleDraggableGreen.node.id="circle"+c+'_'+i
    circleDraggableGreen.drag(move, start, stop)
  }
}

var circleColorChange = groupBoard.circle(50, 0, 20);
circleColorChange.attr({
  class: "colorchange"
});


