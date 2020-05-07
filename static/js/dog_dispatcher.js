import { DogApp } from './dog_app.js'

// export var DogApp = {
//   playerIndex: 42,
//   rotateUrl: 'undefined'
// };

$(document).ready(function () {
  DogApp.socket = DogApp.io.connect('http://' + document.domain + ':' + location.port);

  DogApp.socket.on('connect', function () {
    var msg = { player: DogApp.playerIndex, event: 'browserConnected' };
    DogApp.socket.emit('event', msg);
  });

  DogApp.socket.on('json', function (json) {
    console.log('Received "json": ' + JSON.stringify(json));
    for (var i = 0; i < json.length; i++) { 
      var command = json[i]
      var svg_id = command['svg_id']
      if (svg_id) {
        var svg_element = $(svg_id);
        attr_set = command['attr_set']
        if (attr_set) {
          var elements = svg_element.each(function () {
            for (var attr_name in attr_set) {
              attr_value = attr_set[attr_name];
              this.setAttribute(attr_name, attr_value);
            };
          });
        }
        var transform = command['transform']
        if (transform) {
          DogApp.moveCircle(transform)              
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
          var elements = html_element.each(function () {
            for (var attr_name in attr_set) {
              var attr_value = attr_set[attr_name];
              $(this).attr(attr_name, attr_value)
            };
          });
        }
        continue
      }
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
      name_element = $('input#player0_textfield_name');
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

