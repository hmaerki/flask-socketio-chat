
$(document).ready(function () {
  DogApp.socket = io.connect('http://' + document.domain + ':' + location.port);

  DogApp.socket.on('connect', function () {
    var msg = { room: DogApp.ROOM, event: 'browserConnected' };
    DogApp.socket.emit('event', msg);
  });

  DogApp.socket.on('json', function (json) {

    var playerNames = json['playerNames']
    if (playerNames) {
      playerNames.forEach(function (playerName, index) {
        var svg_element = $('text#'+index+'name')
        svg_element.text(playerName)
      });
    }

    var caluclateCardOpacity = function(x, y) {
      if (y > 100) {
        return 0.0
      } else {
        d = Math.abs(x)+Math.abs(y)
        return 0.05*(d-25)
      }
    }

    var opacityCard = function(groupCard) {
      m = groupCard.transform().localMatrix
      x = m.e
      y = m.f

      // TODO: Add transformation for rotation
      opacity = caluclateCardOpacity(x=x, y=y)
      var cardMask = groupCard.select('rect#mask')
      cardMask.attr({ opacity: opacity})
    }

    var card = json['card']
    if (card) {
      var idnum = card[0]
      var angle = card[1]
      var x = card[2]
      var y = card[3]

      var svgGroupCard = $('g#'+idnum+'card')

      // var svgGroupBoard = $('g.board')
      // svgLastElement = svgGroupBoard.last()
      // svgLastElement.after(svgGroupCard)

      // var svgGroupBoard = svgGroupCard.parent()
      // svgLastElement = svgGroupBoard.last()
      // svgLastElement.after(svgGroupCard)

      svgGroupCard.each(function () {
        // var svgGroupBoard = $(this).parent()
        // svgLastElement = svgGroupBoard.last()
        // svgLastElement.after(this)
        var groupCard = Snap(this)
        groupCard.attr({
          transform: 't'+x+','+y+'r'+angle+' 0 0',
        });
        opacityCard(groupCard);

        // Move card to top
        // groupBoard.remove(groupCard)
        groupBoard.append(groupCard)
      });


  
      // Show this card on the top
      // svgLastElement = groupBoard.last()

      // groupCard = Snap(svgGroupCard.node)
      // groupBoard.append(groupCard)
    }

    var cards = json['cards']
    if (cards) {
      // Remove existing cards
      $('g.card').remove()

      cards.forEach(function (card_attrs, i) {
        var idnum = card_attrs[0]
        var angle = card_attrs[1]
        var x = card_attrs[2]
        var y = card_attrs[3]
        var filebase = card_attrs[4]
        var descriptionI18N = card_attrs[5]

        id = idnum+'card'
        var groupCard = groupBoard.g()
        groupCard.node.id = id
        groupCard.attr({
          class:'card',
        })
        groupCard.drag(card_drag_move, card_drag_start, card_drag_stop);

        groupCard.image(
          "/static/img/cards/" + filebase + ".svg",
          -DogApp.CARD_WIDTH/2,
          -DogApp.CARD_HEIGHT/2,
          DogApp.CARD_WIDTH,
          DogApp.CARD_HEIGHT
        );
        var svgMask = groupCard.rect(
          -DogApp.CARD_WIDTH/2,
          -DogApp.CARD_HEIGHT/2,
          DogApp.CARD_WIDTH,
          DogApp.CARD_HEIGHT,
          3 // radius
        );
        svgMask.node.id = 'mask'
        opacity = caluclateCardOpacity(x, y)
        svgMask.attr({
          // stroke: 'black', 'stroke-width': 0.5,
          fill: 'gray',
          opacity: opacity,
        });

        // TODO: Prevent help text to be displayed if card is hidden (or opacity<=0.0)
        var title = Snap.parse('<title>' + descriptionI18N + '</title>');
        groupCard.append(title);

        groupCard.animate({'transform': 't'+x+','+y+'r'+angle+',0,0'}, 3000, mina.backout);
      });
    }

    for (var i = 0; i < json.length; i++) { 
      var command = json[i]
      var svg_id = command['svg_id']
      if (svg_id) {
        var svg_element = $(svg_id);
        attr_set = command['attr_set']
        if (attr_set) {
          svg_element.each(function () {
            for (var attr_name in attr_set) {
              attr_value = attr_set[attr_name];
              this.setAttribute(attr_name, attr_value);
            };
          });
        }
        marble = command['marble']
        if (marble) {
          x = marble[0]
          y = marble[1]
          svg_element.each(function () {
            this.setAttribute('x', x);
            this.setAttribute('y', y);
          });
        }
        continue
      }
      console.log('Unknown command: ' + command);
    };
  });

});

