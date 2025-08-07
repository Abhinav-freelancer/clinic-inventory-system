const express = require('express');
const http = require('http');
const path = require('path');
const { Server } = require('socket.io');
const socketHandler = require('./socket');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = process.env.PORT || 3000;

// Serve static files from public directory
app.use(express.static(path.join(__dirname, '../public')));

// Use socket handler for signaling
socketHandler(io);

server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
