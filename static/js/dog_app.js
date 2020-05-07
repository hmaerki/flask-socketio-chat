// import { DogApp } from './dog_dispatcher.js'

export var DogApp = {
  io: null,
  playerIndex: 42,
  rotateUrl: 'undefined'
};

export var setPlayer = function(playerIndex, rotateUrl) {
  DogApp.playerIndex = playerIndex;
  DogApp.rotateUrl = rotateUrl;
}

export var setIo = function(io) {
  DogApp.io = io;
}
