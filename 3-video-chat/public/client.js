const socket = io();

const localVideo = document.getElementById('local-video');
const remoteVideos = [
  document.getElementById('remote-video-1'),
  document.getElementById('remote-video-2')
];
const roomInput = document.getElementById('room-input');
const joinBtn = document.getElementById('join-btn');
const errorMsg = document.getElementById('error-msg');
const roomSelection = document.getElementById('room-selection');
const videoChat = document.getElementById('video-chat');
const toggleVideoBtn = document.getElementById('toggle-video');
const toggleAudioBtn = document.getElementById('toggle-audio');

let localStream = null;
let peers = {};
let roomId = null;
let videoEnabled = true;
let audioEnabled = true;

const configuration = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    // TURN server config can be added here if available
  ]
};

joinBtn.onclick = async () => {
  const code = roomInput.value.trim();
  if (!code) {
    errorMsg.textContent = 'Please enter a room code.';
    return;
  }
  errorMsg.textContent = '';
  roomId = code;
  await startLocalStream();
  socket.emit('join-room', roomId);
  roomSelection.classList.add('hidden');
  videoChat.classList.remove('hidden');
};

async function startLocalStream() {
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;
  } catch (err) {
    errorMsg.textContent = 'Could not access camera and microphone.';
    console.error(err);
  }
}

toggleVideoBtn.onclick = () => {
  if (!localStream) return;
  videoEnabled = !videoEnabled;
  localStream.getVideoTracks().forEach(track => track.enabled = videoEnabled);
  toggleVideoBtn.textContent = videoEnabled ? 'Turn Video Off' : 'Turn Video On';
};

toggleAudioBtn.onclick = () => {
  if (!localStream) return;
  audioEnabled = !audioEnabled;
  localStream.getAudioTracks().forEach(track => track.enabled = audioEnabled);
  toggleAudioBtn.textContent = audioEnabled ? 'Turn Audio Off' : 'Turn Audio On';
};

socket.on('room-full', () => {
  errorMsg.textContent = 'Room is full. Cannot join.';
  leaveRoom();
});

socket.on('all-users', (users) => {
  users.forEach(userId => {
    createPeerConnection(userId, true);
  });
});

socket.on('user-joined', (userId) => {
  createPeerConnection(userId, false);
});

socket.on('signal', async (data) => {
  const { from, signal } = data;
  if (!peers[from]) {
    createPeerConnection(from, false);
  }
  const peer = peers[from];
  if (signal.type === 'offer') {
    await peer.setRemoteDescription(new RTCSessionDescription(signal));
    const answer = await peer.createAnswer();
    await peer.setLocalDescription(answer);
    socket.emit('signal', { to: from, from: socket.id, signal: peer.localDescription });
  } else if (signal.type === 'answer') {
    await peer.setRemoteDescription(new RTCSessionDescription(signal));
  } else if (signal.candidate) {
    try {
      await peer.addIceCandidate(new RTCIceCandidate(signal.candidate));
    } catch (e) {
      console.error('Error adding received ice candidate', e);
    }
  }
});

socket.on('user-left', (userId) => {
  if (peers[userId]) {
    peers[userId].close();
    delete peers[userId];
    removeRemoteVideo(userId);
  }
});

function createPeerConnection(userId, isInitiator) {
  const peer = new RTCPeerConnection(configuration);
  peers[userId] = peer;

  localStream.getTracks().forEach(track => peer.addTrack(track, localStream));

  peer.onicecandidate = (event) => {
    if (event.candidate) {
      socket.emit('signal', { to: userId, from: socket.id, signal: { candidate: event.candidate } });
    }
  };

  peer.ontrack = (event) => {
    addRemoteStream(userId, event.streams[0]);
  };

  if (isInitiator) {
    peer.onnegotiationneeded = async () => {
      try {
        const offer = await peer.createOffer();
        await peer.setLocalDescription(offer);
        socket.emit('signal', { to: userId, from: socket.id, signal: peer.localDescription });
      } catch (err) {
        console.error(err);
      }
    };
  }

  peer.onconnectionstatechange = () => {
    if (peer.connectionState === 'disconnected' || peer.connectionState === 'failed' || peer.connectionState === 'closed') {
      peer.close();
      delete peers[userId];
      removeRemoteVideo(userId);
    }
  };
}

function addRemoteStream(userId, stream) {
  let videoEl = null;
  if (!remoteVideos[0].srcObject) {
    videoEl = remoteVideos[0];
  } else if (!remoteVideos[1].srcObject) {
    videoEl = remoteVideos[1];
  }
  if (videoEl) {
    videoEl.srcObject = stream;
  }
}

function removeRemoteVideo(userId) {
  remoteVideos.forEach(videoEl => {
    if (videoEl.srcObject && videoEl.srcObject.id === userId) {
      videoEl.srcObject = null;
    }
  });
}

function leaveRoom() {
  Object.values(peers).forEach(peer => peer.close());
  peers = {};
  if (localStream) {
    localStream.getTracks().forEach(track => track.stop());
    localStream = null;
  }
  roomId = null;
  roomSelection.classList.remove('hidden');
  videoChat.classList.add('hidden');
}
