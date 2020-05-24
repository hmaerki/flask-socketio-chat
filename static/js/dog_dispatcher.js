
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

    var opacityCard = function(groupCard) {
      // Upside down if board flipped m.e + ', ' + m.f
      m1 = groupCard.transform.baseVal[0].matrix
      // console.log('card transform:' + m0.e + ', ' + m0.f)
      x1 = m1.e
      y1 = m1.f

      // m2 = groupBoard.node.transform.baseVal[0].matrix

      // x2 = + m2.a*x1 - m2.c*y1;
      // y2 = - m2.b*x1 + m2.d*y1;
      // console.log('card transform:' + x1 + '/' + y2 + ', ' + x2 + '/' + y2)
    
      x = x1
      y = y1
      if (y > 100) {
        opacity = 0.0
      } else {
        d = Math.abs(x)+Math.abs(y)
        opacity = 0.05*(d-25)
      }

      // var svg_element1 = $(this).find('rect#mask')
      // svg_element1.each(function () {
      //   this.setAttribute('fill', 'red');
      //   s = Snap(this)
      //   s.attr({
      //     'fill': '#00F',
      //     'opacity': 1.0,
      //   })
      // });

      var cardMask = $(groupCard).find('rect#mask')
      cardMask.each(function () {
        s = Snap(this)
        s.attr({ opacity: opacity})
      });

      // var cm = Snap(cardMask.node)
      // cm.attr({ opacity: 1.0, fill: 'red' })
      // console.log('opacity:' + opacity)
    }

    var placeCard = function(id, card) {
      var angle = card[0]
      var x = card[1]
      var y = card[2]
      var svg_element = $('g#'+id+'card')
      svg_element.each(function () {
        this.setAttribute('transform', 'translate('+x+','+y+') rotate('+angle+' 0 0)');
        opacityCard(this);
      });
    }
  
    var card = json['card']
    if (card) {
      placeCard(card[0], card[1])
    }

    var cards = json['cards']
    if (cards) {
      // Remove existing cards
      $('g.card').remove()

      cards.forEach(function (card, i) {
        var angle = card[0]
        var x = card[1]
        var y = card[2]
        var filebase = card[3]
        var descriptionI18N = card[4]

        id = i+'card'
        var groupCard = groupBoard.g()
        groupCard.node.id = id
        groupCard.attr({
          class:'card',
          // https://www.sitepoint.com/advanced-snap-svg/
          // mask: rectPlayerClip,
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
        // svgMask.attr({
        //   mask: rectPlayerClip,
        // });
        svgMask.node.id = 'mask'
        svgMask.attr({ stroke: 'black', 'stroke-width': 0.5, fill: 'gray', 'opacity': 1.0 });

        // groupCard.attr({'transform': 't'+x+','+y+'r'+angle+',0,0'});
        groupCard.animate({'transform': 't'+x+','+y+'r'+angle+',0,0'}, 3000, mina.backout);

        var title = Snap.parse('<title>' + descriptionI18N + '</title>');
        groupCard.append( title );
      });
    }

      // console.log('Received "json": ' + JSON.stringify(json));
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
      var html_id = command['html_id']
      if (html_id) {
        // Correspnds to:
        // 'call_html': {
        //     'id': '#time',
        //     'calls': {
        //         'html': str_time
        //     }
        // }
        // $('#time').html(str_time);
        var html_element = $(html_id);
        var html_calls = command['call']
        if (html_calls) {
          for (var html_call in html_calls) {
            html_call_argument = html_calls[html_call];
            html_element[html_call].call(html_element, html_call_argument)
          };
        }
        var attr_set = command['attr_set']
        if (attr_set) {
          html_element.each(function () {
            for (var attr_name in attr_set) {
              var attr_value = attr_set[attr_name];
              $(this).attr(attr_name, attr_value)
            };
          });
        }
        var attr_set = command['html']
        if (attr_set) {
          html_element.each(function () {
            $(this).html(attr_set)
          });
        }
        continue
      }
      console.log('Unknown command: ' + command);
    };
  });

  DogApp.socket.on('message', function (msg) {
    // console.log('Received "message": ' + msg);
    var i = msg.indexOf(':');
    var method = msg.slice(0, i)
    var text = msg.slice(i + 1)
    if (method == 'MESSAGE') {
      $('#messages').append('<li>' + text + '</li>');
    }
  });

});

