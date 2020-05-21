
$(document).ready(function () {
  DogApp.socket = io.connect('http://' + document.domain + ':' + location.port);

  DogApp.socket.on('connect', function () {
    var msg = { player: DogApp.playerIndex, event: 'browserConnected' };
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

    var cards = json['cards']
    if (cards) {
      cards.forEach(function (card, index) {
        var x = card[0]
        var y = card[1]
        // console.log('card: ' + card + ', x: ' + x)
        var svg_element = $('#'+index+'card')
        svg_element.each(function () {
          this.setAttribute('x', x);
          this.setAttribute('y', y);
        });
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
    console.log('Received "message": ' + msg);
    var i = msg.indexOf(':');
    var method = msg.slice(0, i)
    var text = msg.slice(i + 1)
    if (method == 'MESSAGE') {
      $('#messages').append('<li>' + text + '</li>');
    }
  });

  $(':button').on('click', function () {
    var click_msg = { player: DogApp.playerIndex, event: this.id, card: this.name };
    if (this.id === 'setName') {
      // Special case: SetName Button
      name_element = $(`input#player${DogApp.playerIndex}_textfield_name`);
      click_msg['name'] = name_element.val();
    }
    else
    {
      // The name-attribute is misued to store the card number
      click_msg['card'] = this.name;
    }
    DogApp.socket.emit('event', click_msg);

    if (this.id === 'rotateBoard') {
      // Special case: RotateBoard Button
      location.replace(DogApp.rotateUrl)
    }

  });
});

