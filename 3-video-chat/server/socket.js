module.exports = function(io) {
  const rooms = {};

  io.on('connection', (socket) => {
    console.log('User connected:', socket.id);

    socket.on('join-room', (roomId) => {
      if (!rooms[roomId]) {
        rooms[roomId] = [];
      }
      const clients = rooms[roomId];

      if (clients.length >= 3) {
        socket.emit('room-full');
        return;
      }

      clients.push(socket.id);
      socket.join(roomId);
      socket.roomId = roomId;

      console.log(`User ${socket.id} joined room ${roomId}`);

      // Notify existing users about new user
      socket.to(roomId).emit('user-joined', socket.id);

      // Send existing users to the new user
      socket.emit('all-users', clients.filter(id => id !== socket.id));

      // Close room if 3 users joined
      if (clients.length === 3) {
        io.in(roomId).emit('room-full');
      }
    });

    socket.on('signal', (data) => {
      const { to, from, signal } = data;
      io.to(to).emit('signal', { from, signal });
    });

    socket.on('disconnect', () => {
      const roomId = socket.roomId;
      if (roomId && rooms[roomId]) {
        rooms[roomId] = rooms[roomId].filter(id => id !== socket.id);
        socket.to(roomId).emit('user-left', socket.id);
        console.log(`User ${socket.id} left room ${roomId}`);

        if (rooms[roomId].length === 0) {
          delete rooms[roomId];
          console.log(`Room ${roomId} deleted`);
        }
      }
    });
  });
};
