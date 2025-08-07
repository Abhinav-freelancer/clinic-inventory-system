import { useState, useEffect } from 'react';

export default function App() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [branch, setBranch] = useState('');
  const [year, setYear] = useState('1');
  const [interests, setInterests] = useState('');
  const [posts, setPosts] = useState([]);
  const [communities, setCommunities] = useState([
    { id: 1, name: 'Tech', members: 245 },
    { id: 2, name: 'Music', members: 130 },
    { id: 3, name: 'Placements', members: 320 },
    { id: 4, name: 'Events', members: 98 },
  ]);
  const [activeTab, setActiveTab] = useState('feed');
  const [searchQuery, setSearchQuery] = useState('');
  const [reportedPosts, setReportedPosts] = useState([]);

  // Mock Data for Posts
  useEffect(() => {
    setPosts([
      {
        id: 1,
        author: "Raj Patel",
        branch: "CSE",
        year: "2",
        content: "Just finished my first hackathon! 🚀",
        media: "https://placehold.co/600x400?text=Hackathon+Project",
        likes: 42,
        comments: 8,
        shared: 5,
        community: "Tech"
      },
      {
        id: 2,
        author: "Priya Sharma",
        branch: "ECE",
        year: "3",
        content: "Looking for study group partners for DBMS.",
        media: null,
        likes: 15,
        comments: 3,
        shared: 2,
        community: "Placements"
      },
      {
        id: 3,
        author: "Amit Verma",
        branch: "EEE",
        year: "1",
        content: "Anyone going to the music fest this weekend?",
        media: " https://placehold.co/600x400?text=Music+Festival",
        likes: 27,
        comments: 6,
        shared: 4,
        community: "Music"
      }
    ]);
  }, []);

  const handleRegister = (e) => {
    e.preventDefault();
    if (!email.endsWith('@vit.ac.in')) {
      alert("Only VIT Chennai students can register.");
      return;
    }

    const newUser = {
      email,
      name,
      branch,
      year,
      interests: interests.split(',').map(i => i.trim()),
      joinedCommunities: []
    };
    setUser(newUser);
    setEmail('');
    setPassword('');
    setName('');
    setBranch('');
    setYear('1');
    setInterests('');
    setActiveTab('feed');
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (!email.endsWith('@vit.ac.in')) {
      alert("Invalid VIT email.");
      return;
    }
    const existingUser = {
      email,
      name: "John Doe",
      branch: "CSE",
      year: "2",
      interests: ["coding", "tech"],
      joinedCommunities: ["Tech"]
    };
    setUser(existingUser);
    setEmail('');
    setPassword('');
    setActiveTab('feed');
  };

  const handleLogout = () => {
    setUser(null);
    setActiveTab('login');
  };

  const handlePostSubmit = (newPost) => {
    setPosts(prev => [
      {
        id: Date.now(),
        ...newPost
      },
      ...prev
    ]);
  };

  const handleReportPost = (postId) => {
    const post = posts.find(p => p.id === postId);
    setReportedPosts(prev => [...prev, post]);
    setPosts(prev => prev.filter(p => p.id !== postId));
    alert("Post reported successfully.");
  };

  const renderLoginForm = () => (
    <div className="auth-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="VIT Email (@vit.ac.in)"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      <p>
        Don't have an account?{" "}
        <button onClick={() => setActiveTab('register')} className="link-btn">
          Register
        </button>
      </p>
    </div>
  );

  const renderRegisterForm = () => (
    <div className="auth-container">
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="VIT Email (@vit.ac.in)"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <select
          value={branch}
          onChange={(e) => setBranch(e.target.value)}
          required
        >
          <option value="">Select Branch</option>
          <option value="CSE">Computer Science</option>
          <option value="ECE">Electronics</option>
          <option value="EEE">Electrical</option>
          <option value="MECH">Mechanical</option>
          <option value="Civil">Civil</option>
        </select>
        <select
          value={year}
          onChange={(e) => setYear(e.target.value)}
          required
        >
          <option value="1">1st Year</option>
          <option value="2">2nd Year</option>
          <option value="3">3rd Year</option>
          <option value="4">4th Year</option>
        </select>
        <input
          type="text"
          placeholder="Interests (comma-separated)"
          value={interests}
          onChange={(e) => setInterests(e.target.value)}
        />
        <button type="submit">Register</button>
      </form>
      <p>
        Already have an account?{" "}
        <button onClick={() => setActiveTab('login')} className="link-btn">
          Login
        </button>
      </p>
    </div>
  );

  const renderFeed = () => (
    <div className="main-content">
      <h1>Welcome, {user.name}</h1>

      {/* Create Post */}
      <CreatePostForm onPostSubmit={handlePostSubmit} user={user} />

      {/* Feed Posts */}
      <div className="post-list">
        {posts.map(post => (
          <PostCard key={post.id} post={post} onReport={() => handleReportPost(post.id)} />
        ))}
      </div>
    </div>
  );

  const renderCommunities = () => (
    <div className="main-content">
      <h1>Join Communities</h1>
      <div className="community-grid">
        {communities.map(comm => (
          <CommunityCard key={comm.id} community={comm} />
        ))}
      </div>
    </div>
  );

  const renderSearch = () => (
    <div className="main-content">
      <h1>Search Students</h1>
      <div className="search-box">
        <input
          type="text"
          placeholder="Search by name, branch, or year..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      <p>Type above to search students.</p>
    </div>
  );

  const renderAdminPanel = () => (
    <div className="main-content">
      <h1>Admin Panel - Reported Posts</h1>
      {reportedPosts.length === 0 ? (
        <p>No reported posts yet.</p>
      ) : (
        <div className="post-list">
          {reportedPosts.map(post => (
            <PostCard key={post.id} post={post} showActions={false} />
          ))}
        </div>
      )}
    </div>
  );

  const renderMainContent = () => {
    switch (activeTab) {
      case 'feed':
        return renderFeed();
      case 'communities':
        return renderCommunities();
      case 'search':
        return renderSearch();
      case 'admin':
        return renderAdminPanel();
      default:
        return renderFeed();
    }
  };

  if (!user) {
    return activeTab === 'login' ? renderLoginForm() : renderRegisterForm();
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>VIT Connect</h1>
        <nav>
          <button onClick={() => setActiveTab('feed')}>Feed</button>
          <button onClick={() => setActiveTab('communities')}>Communities</button>
          <button onClick={() => setActiveTab('search')}>Search</button>
          <button onClick={() => setActiveTab('admin')}>Admin</button>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </nav>
      </header>

      {/* Main Content */}
      {renderMainContent()}
    </div>
  );
}

// Components

function CreatePostForm({ onPostSubmit, user }) {
  const [content, setContent] = useState('');
  const [media, setMedia] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    onPostSubmit({
      author: user.name,
      branch: user.branch,
      year: user.year,
      content,
      media: media || null,
      likes: 0,
      comments: 0,
      shared: 0,
      community: "General"
    });

    setContent('');
    setMedia('');
  };

  return (
    <form onSubmit={handleSubmit} className="create-post-form">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="What's on your mind?"
        required
        rows={3}
      />
      <input
        type="url"
        value={media}
        onChange={(e) => setMedia(e.target.value)}
        placeholder="Image or video URL (optional)"
      />
      <button type="submit">Post</button>
    </form>
  );
}

function PostCard({ post, onReport, showActions = true }) {
  return (
    <div className="post-card">
      <div className="post-header">
        <div className="avatar">{post.author.charAt(0)}</div>
        <div>
          <strong>{post.author}</strong>
          <br />
          <small>{post.branch} • Year {post.year}</small>
        </div>
      </div>
      <p>{post.content}</p>
      {post.media && <img src={post.media} alt="Post" />}
      <p className="community-tag">#{post.community}</p>
      {showActions && (
        <div className="post-actions">
          <button>Like ({post.likes})</button>
          <button>Comment ({post.comments})</button>
          <button>Share ({post.shared})</button>
          <button onClick={onReport} className="report-btn">Report</button>
        </div>
      )}
    </div>
  );
}

function CommunityCard({ community }) {
  return (
    <div className="community-card">
      <h3>{community.name}</h3>
      <p>{community.members} members</p>
      <button>Join</button>
    </div>
  );
}

// Styles

const styles = `
.app {
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
}

.header {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header h1 {
  color: #0077cc;
}

.header nav button {
  margin-right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.logout-btn {
  color: red;
}

.auth-container {
  max-width: 400px;
  margin: 4rem auto;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.auth-container h2 {
  text-align: center;
  margin-bottom: 1rem;
}

.auth-container input {
  width: 100%;
  padding: 0.75rem;
  margin: 0.5rem 0;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.auth-container button {
  width: 100%;
  padding: 0.75rem;
  background-color: #0077cc;
  color: white;
  border: none;
  border-radius: 4px;
  margin-top: 1rem;
  cursor: pointer;
}

.link-btn {
  background: none;
  border: none;
  color: #0077cc;
  text-decoration: underline;
  cursor: pointer;
}

.main-content {
  padding: 2rem;
}

.create-post-form textarea {
  width: 100%;
  resize: none;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.create-post-form input[type="url"] {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.post-list {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.post-card {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 0 5px rgba(0,0,0,0.1);
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.avatar {
  width: 30px;
  height: 30px;
  background: #0077cc;
  color: white;
  font-weight: bold;
  text-align: center;
  border-radius: 50%;
  margin-right: 1rem;
}

.community-tag {
  font-style: italic;
  color: #666;
}

.post-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

.report-btn {
  color: red;
  background: none;
  border: none;
  cursor: pointer;
}

.community-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.community-card {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 0 5px rgba(0,0,0,0.1);
  text-align: center;
}

.community-card button {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #0077cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-box input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

@media (max-width: 600px) {
  .header nav {
    flex-direction: column;
    align-items: flex-start;
  }
}
`;

// Inject CSS into the document head
const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);