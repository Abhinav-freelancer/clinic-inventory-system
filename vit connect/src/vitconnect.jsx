import React, { useState, useEffect, createContext, useContext, useRef } from 'react';

// Mock data for users, posts, communities
const mockUsers = [
  {
    id: 1,
    name: "Aryan Mehta",
    email: "aryan@vit.ac.in",
    branch: "CSE",
    year: "3rd Year",
    interests: ["Web Dev", "Music"],
    profilePic: "https://picsum.photos/id/237/200/200 "
  },
  {
    id: 2,
    name: "Priya Sharma",
    email: "priya@vit.ac.in",
    branch: "ECE",
    year: "2nd Year",
    interests: ["Photography", "Tech"],
    profilePic: "https://picsum.photos/id/238/200/200 "
  },
];

const mockPosts = [
  {
    id: 1,
    userId: 1,
    content: "Just built a cool new app! 🚀",
    media: "https://picsum.photos/id/1019/400/300 ",
    likes: 15,
    comments: [
      { user: "Priya Sharma", text: "Looks awesome!" }
    ],
    shared: false,
    timestamp: "2 hours ago"
  },
  {
    id: 2,
    userId: 2,
    content: "Exploring the campus with my friends today 😊",
    media: "https://picsum.photos/id/1025/400/300 ",
    likes: 8,
    comments: [],
    shared: false,
    timestamp: "5 hours ago"
  },
];

const mockCommunities = [
  { id: 1, name: "Tech Club", members: 120 },
  { id: 2, name: "Music Lovers", members: 80 },
  { id: 3, name: "Placement Prep", members: 200 },
];

// Auth Context
const AuthContext = createContext();

function App() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState("");
  const [isRegistered, setIsRegistered] = useState(false);
  const [activeTab, setActiveTab] = useState("feed");
  const [posts, setPosts] = useState(mockPosts);
  const [newPostContent, setNewPostContent] = useState("");
  const [newPostMedia, setNewPostMedia] = useState("");

  // Handle login/signup
  const handleLogin = () => {
    if (email.endsWith("@vit.ac.in")) {
      const existingUser = mockUsers.find(u => u.email === email);
      if (existingUser) {
        setUser(existingUser);
        setIsRegistered(true);
      } else {
        setIsRegistered(false);
      }
    } else {
      alert("Please use your VIT Chennai email address.");
    }
  };

  // Create post
  const createPost = () => {
    if (!newPostContent.trim()) return;
    const newPost = {
      id: Date.now(),
      userId: user.id,
      content: newPostContent,
      media: newPostMedia || "",
      likes: 0,
      comments: [],
      shared: false,
      timestamp: "just now"
    };
    setPosts([newPost, ...posts]);
    setNewPostContent("");
    setNewPostMedia("");
    setActiveTab("feed");
  };

  // Like post
  const likePost = (postId) => {
    setPosts(posts.map(post =>
      post.id === postId ? { ...post, likes: post.likes + 1 } : post
    ));
  };

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      <div className="min-h-screen bg-gray-100">
        {!user ? (
          <Login onLogin={handleLogin} email={email} setEmail={setEmail} isRegistered={isRegistered} />
        ) : (
          <>
            <Header activeTab={activeTab} setActiveTab={setActiveTab} />
            <main className="container mx-auto px-4 py-6">
              {activeTab === "feed" && (
                <Feed posts={posts} onLike={likePost} onCreatePost={createPost} newPostContent={newPostContent} 
                  setNewPostContent={setNewPostContent} newPostMedia={newPostMedia} setNewPostMedia={setNewPostMedia} />
              )}
              {activeTab === "communities" && <Communities communities={mockCommunities} />}
              {activeTab === "search" && <Search users={mockUsers} />}
              {activeTab === "profile" && <Profile user={user} />}
            </main>
            <Footer />
          </>
        )}
      </div>
    </AuthContext.Provider>
  );
}

// Login Component
function Login({ onLogin, email, setEmail, isRegistered }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">VIT Connect</h1>
        <p className="text-center text-gray-600 mb-6">Connect with fellow VIT Chennai students</p>
        <input
          type="email"
          placeholder="Enter your @vit.ac.in email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-md mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={onLogin}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-md transition duration-200"
        >
          Continue
        </button>
        {!isRegistered && (
          <p className="mt-4 text-sm text-gray-600 text-center">
            You'll need to complete your profile after logging in.
          </p>
        )}
      </div>
    </div>
  );
}

// Header Component
function Header({ activeTab, setActiveTab }) {
  const { user } = useContext(AuthContext);

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-blue-600">VIT Connect</h1>
        <nav className="hidden md:flex space-x-6">
          {["feed", "communities", "search", "profile"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`capitalize font-medium transition duration-200 ${
                activeTab === tab ? "text-blue-600" : "text-gray-600 hover:text-blue-500"
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
        <div className="flex items-center space-x-4">
          <img
            src={user?.profilePic}
            alt="Profile"
            className="w-10 h-10 rounded-full object-cover"
          />
        </div>
      </div>
    </header>
  );
}

// Feed Component
function Feed({ posts, onLike, onCreatePost, newPostContent, setNewPostContent, newPostMedia, setNewPostMedia }) {
  const [showCreatePost, setShowCreatePost] = useState(false);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex items-start space-x-3">
          <img
            src="https://picsum.photos/id/237/200/200 "
            alt="Your avatar"
            className="w-10 h-10 rounded-full object-cover"
          />
          <div className="flex-1">
            <textarea
              placeholder="What's on your mind?"
              value={newPostContent}
              onChange={(e) => setNewPostContent(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows="3"
            ></textarea>
            <input
              type="text"
              placeholder="Image URL (optional)"
              value={newPostMedia}
              onChange={(e) => setNewPostMedia(e.target.value)}
              className="w-full p-2 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex justify-end mt-2">
              <button
                onClick={onCreatePost}
                disabled={!newPostContent.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200 disabled:opacity-50"
              >
                Post
              </button>
            </div>
          </div>
        </div>
      </div>

      {posts.map((post) => (
        <div key={post.id} className="bg-white rounded-lg shadow-md p-4 mb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <img
                src="https://picsum.photos/id/237/200/200 "
                alt="User"
                className="w-10 h-10 rounded-full object-cover"
              />
              <div>
                <h3 className="font-semibold">{mockUsers.find(u => u.id === post.userId)?.name}</h3>
                <p className="text-sm text-gray-500">{post.timestamp}</p>
              </div>
            </div>
            <button className="text-gray-500 hover:text-gray-700">
              <DotsIcon />
            </button>
          </div>

          <p className="mt-3 text-gray-800">{post.content}</p>

          {post.media && (
            <div className="mt-3">
              {post.media.includes("video") ? (
                <video src={post.media} controls className="w-full rounded-lg" />
              ) : (
                <img src={post.media} alt="Post" className="w-full rounded-lg" />
              )}
            </div>
          )}

          <div className="mt-4 flex justify-between text-sm">
            <button
              onClick={() => onLike(post.id)}
              className="flex items-center space-x-1 text-gray-600 hover:text-blue-600"
            >
              <HeartIcon filled={false} />
              <span>{post.likes}</span>
            </button>
            <button className="flex items-center space-x-1 text-gray-600 hover:text-green-600">
              <CommentIcon />
              <span>{post.comments.length}</span>
            </button>
            <button className="flex items-center space-x-1 text-gray-600 hover:text-purple-600">
              <ShareIcon />
              <span>Share</span>
            </button>
          </div>

          {post.comments.length > 0 && (
            <div className="mt-4 border-t pt-3">
              {post.comments.map((comment, index) => (
                <div key={index} className="flex items-start space-x-2 mt-2">
                  <img
                    src="https://picsum.photos/id/238/200/200 "
                    alt="User"
                    className="w-6 h-6 rounded-full object-cover"
                  />
                  <div>
                    <h4 className="font-semibold text-sm">{comment.user}</h4>
                    <p className="text-sm text-gray-700">{comment.text}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-3 flex items-center">
            <input
              type="text"
              placeholder="Add a comment..."
              className="flex-1 p-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// Communities Component
function Communities({ communities }) {
  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Join Communities</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {communities.map((community) => (
          <div key={community.id} className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-xl font-semibold">{community.name}</h3>
            <p className="text-gray-600">{community.members} members</p>
            <button className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200">
              Join
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

// Search Component
function Search({ users }) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.branch.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.year.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Find Students</h2>
      <input
        type="text"
        placeholder="Search by name, branch, or year..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-6"
      />

      <div className="space-y-4">
        {filteredUsers.map((user) => (
          <div key={user.id} className="bg-white rounded-lg shadow-md p-4 flex items-center">
            <img
              src={user.profilePic}
              alt={user.name}
              className="w-12 h-12 rounded-full object-cover mr-4"
            />
            <div>
              <h3 className="font-semibold">{user.name}</h3>
              <p className="text-sm text-gray-600">{user.branch}, {user.year}</p>
              <div className="flex mt-2 space-x-2">
                {user.interests.map((interest, i) => (
                  <span key={i} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    {interest}
                  </span>
                ))}
              </div>
            </div>
            <button className="ml-auto px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200 text-sm">
              Follow
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

// Profile Component
function Profile({ user }) {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex flex-col md:flex-row items-center md:items-start">
          <img
            src={user.profilePic}
            alt={user.name}
            className="w-32 h-32 rounded-full object-cover mb-4 md:mb-0 md:mr-6"
          />
          <div className="text-center md:text-left">
            <h1 className="text-2xl font-bold">{user.name}</h1>
            <p className="text-gray-600">{user.branch}, {user.year}</p>
            <div className="flex flex-wrap justify-center md:justify-start mt-2">
              {user.interests.map((interest, i) => (
                <span key={i} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full mr-2 mb-2">
                  {interest}
                </span>
              ))}
            </div>
            <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200">
              Edit Profile
            </button>
          </div>
        </div>
      </div>

      <h2 className="text-2xl font-bold mt-8 mb-4">Your Posts</h2>
      <div className="bg-white rounded-lg shadow-md p-4">
        <p className="text-gray-600">You haven't posted anything yet.</p>
      </div>
    </div>
  );
}

// Footer Component
function Footer() {
  return (
    <footer className="bg-white shadow-inner mt-8">
      <div className="container mx-auto px-4 py-6 text-center text-gray-600">
        <p>VIT Connect © 2025 - A private social network for VIT Chennai students</p>
      </div>
    </footer>
  );
}

// Icon Components
function HeartIcon({ filled = false }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
    </svg>
  );
}

function CommentIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
    </svg>
  );
}

function ShareIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="18" cy="5" r="3"></circle>
      <circle cx="6" cy="12" r="3"></circle>
      <circle cx="18" cy="19" r="3"></circle>
      <line x1="8.59" y1="13.51" x2="15.42" y2="18.49"></line>
      <line x1="15.41" y1="6.51" x2="8.59" y2="11.49"></line>
    </svg>
  );
}

function DotsIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="1"></circle>
      <circle cx="19" cy="12" r="1"></circle>
      <circle cx="5" cy="12" r="1"></circle>
    </svg>
  );
}

export default App;