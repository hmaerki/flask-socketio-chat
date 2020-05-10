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

  groupBoard.animate({ transform: 'r90,0,0' }, 1000, mina.bounce );





// var snap = Snap();
// Lets create big circle in the middle:
var circleColorChange = snap.circle(10, 10, 20);
circleColorChange.attr({
  class: "colorchange"
});

var rectBorder = snap.rect(-50, -50, 100, 100, 10, 10)
rectBorder.attr({
  // fill: "#888",
  fill: "#f00",
  stroke: "#000",
  strokeWidth: 1,
  opacity: 0.5,
})

var circleDraggableGreen = snap.circle(0, 0, 50);
// By default its black, lets change its attributes
circleDraggableGreen.attr({
  fill: "#bada55",
  stroke: "#000",
  strokeWidth: 5,
  class: "draggable"
});

DogApp.moveCircle = function (transform) {
  // transform = circleDraggableGreen.transform().local + (circleDraggableGreen.transform().local ? "T" : "t") + [dx, dy]
  console.log("transform: " + transform)
  circleColorChange.attr({
    transform: transform
  });
  board.animate({ transform: transform}, 100)
}


//
// Moving the cicle will emit messages to the server
//
var move = function (dx, dy) {
  var transform = this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, dy]
  this.attr({
    transform: transform
  });
  // DogApp.socket.emit("move", {id: this.id, cx: this.node.getAttribute("cx"), dx: dx});
  var move_msg = { id: this.id, transform: transform }
  DogApp.socket.emit("move", move_msg);
}

var start = function () {
  this.data('origTransform', this.transform().local);
  DogApp.move_last_s = 0.0
}
var stop = function () {
  console.log('finished dragging');
}
circleDraggableGreen.drag(move, start, stop)
//board.drag()
