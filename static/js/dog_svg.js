// http://snapsvg.io/docs/
// http://snapsvg.io/demos/
// http://snapsvg.io/start/
// http://svg.dabbles.info/snaptut-responsive
// https://wiki.selfhtml.org/wiki/SVG/Tutorials/Einstieg/SVG_in_responsiven_Webseiten
// https://css-tricks.com/scale-svg/

// First lets create our drawing surface out of existing SVG element
// If you want to create new surface just provide dimensions
// like s = Snap(800, 600);
// var s = Snap("#svg");
var s = Snap("#svg");
// var s = Snap();
// Lets create big circle in the middle:
var circleColorChange = s.circle(10, 10, 20);
circleColorChange.attr({
  class: "colorchange"
});

var circleDraggableGreen = s.circle(150, 150, 100);
// By default its black, lets change its attributes
circleDraggableGreen.attr({
  fill: "#bada55",
  stroke: "#000",
  strokeWidth: 5,
  class: "draggable"
});

// Now lets create another small circle:
var circleB = s.circle(100, 150, 70);
// Lets put this small circle and another one into a group:
var discs = s.group(circleB, s.circle(200, 150, 70));
// Now we can change attributes for the whole group
discs.attr({
  fill: "#fff"
});

var board = s.image("static/img/20030731_181107_dog_4.jpg", 10, 10, 200, 200);
board.attr({
  // x: 10,
  // y: 10,
  // width: 200,
  // height: 200,
  class: "draggable"
})

// Despite our small circle now is a part of a group
// and a part of a mask we could still access it:
circleB.animate({ r: 50 }, 1000);
// We don’t have reference for second small circle,
// but we could easily grab it with CSS selectors:
discs.select("circle:nth-child(2)").animate({ r: 50 }, 1000);

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
