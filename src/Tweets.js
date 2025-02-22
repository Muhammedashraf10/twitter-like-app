import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { getTweets, postTweet, deleteTweet, updateTweet, loveTweet, commentTweet, retweetTweet, followUser } from './api';

function Tweets() {
  const [tweets, setTweets] = useState([]);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [editTweet, setEditTweet] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [commentTweetId, setCommentTweetId] = useState(null);
  const [commentText, setCommentText] = useState('');
  const [showProfile, setShowProfile] = useState(false);
  const [followUsername, setFollowUsername] = useState('');
  const username = localStorage.getItem('username');
  const navigate = useNavigate();

  useEffect(() => {
    fetchTweets();
    const interval = setInterval(fetchTweets, 10000); // Auto-refresh
    return () => clearInterval(interval);
  }, []);

  const fetchTweets = async () => {
    try {
      const data = await getTweets();
      console.log('Fetched tweets:', data); // Debug: Check loved_by
      setTweets(data);
    } catch (err) {
      toast.error(err.message);
      if (err.message.includes('Unauthorized')) {
        localStorage.clear();
        navigate('/');
      }
    }
  };

  const handlePost = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await postTweet(content);
      setContent('');
      toast.success('Tweet posted successfully!');
      fetchTweets();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (tweetId) => {
    try {
      await deleteTweet(tweetId);
      toast.success('Tweet deleted successfully!');
      fetchTweets();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleEdit = (tweet) => {
    setEditTweet(tweet);
    setEditContent(tweet.content);
  };

  const handleUpdate = async () => {
    try {
      await updateTweet(editTweet.tweet_id, editContent);
      setEditTweet(null);
      setEditContent('');
      toast.success('Tweet updated successfully!');
      fetchTweets();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleLove = async (tweetId) => {
    try {
      const data = await loveTweet(tweetId);
      const action = data.message.includes('loved') ? 'loved' : 'unloved';
      toast.success(`Tweet ${action}! (${data.loves} loves)`);
      await fetchTweets(); // Ensure latest data
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleComment = async (tweetId) => {
    try {
      await commentTweet(tweetId, commentText);
      setCommentTweetId(null);
      setCommentText('');
      toast.success('Comment added successfully!');
      fetchTweets();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleRetweet = async (tweetId) => {
    try {
      await retweetTweet(tweetId);
      toast.success('Tweet retweeted successfully!');
      fetchTweets();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleFollow = async () => {
    try {
      await followUser(followUsername);
      toast.success(`Now following ${followUsername}!`);
      setFollowUsername('');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const logout = () => {
    localStorage.clear();
    navigate('/');
  };

  return (
    <div className="tweets-container">
      <div className="header">
        <h2>Tweets</h2>
        <div className="profile">
          <span onClick={() => setShowProfile(true)} className="username">
            @{username}
          </span>
          <button onClick={logout} className="logout-btn">Logout</button>
        </div>
      </div>
      <form onSubmit={handlePost}>
        <div className="tweet-input">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What's on your mind?"
            maxLength="280"
            required
          />
          <span className="char-count">{280 - content.length}</span>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? <span className="spinner"></span> : 'Post Tweet'}
        </button>
      </form>
      <div className="tweet-list">
        {tweets.map(tweet => (
          <div key={tweet.tweet_id} className="tweet-item">
            <div className="tweet-content">
              <strong>{tweet.username}</strong>: {tweet.content}
              <span className="timestamp">({new Date(tweet.timestamp * 1000).toLocaleString()})</span>
              <span className="loves">❤️ {tweet.loved_by ? tweet.loved_by.length : 0}</span>
              <span className="retweets">🔄 {tweet.retweets ? tweet.retweets.length : 0}</span>
            </div>
            <div className="tweet-actions">
              <button onClick={() => handleLove(tweet.tweet_id)} className="love-btn">
                {tweet.loved_by && tweet.loved_by.includes(username) ? 'Unlove' : 'Love'}
              </button>
              <button onClick={() => handleRetweet(tweet.tweet_id)} className="retweet-btn">Retweet</button>
              <button onClick={() => setCommentTweetId(tweet.tweet_id)}>Comment</button>
              {tweet.username === username && (
                <>
                  <button onClick={() => handleEdit(tweet)}>Edit</button>
                  <button onClick={() => handleDelete(tweet.tweet_id)}>Delete</button>
                </>
              )}
            </div>
            {commentTweetId === tweet.tweet_id && (
              <div className="comment-form">
                <textarea
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  placeholder="Add a comment..."
                  maxLength="280"
                />
                <button onClick={() => handleComment(tweet.tweet_id)}>Post Comment</button>
                <button onClick={() => setCommentTweetId(null)}>Cancel</button>
              </div>
            )}
            {tweet.comments && tweet.comments.length > 0 && (
              <div className="comments">
                {tweet.comments.map(comment => (
                  <div key={comment.comment_id} className="comment">
                    <strong>{comment.username}</strong>: {comment.text}
                    <span className="timestamp">({new Date(comment.timestamp * 1000).toLocaleString()})</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      {editTweet && (
        <div className="modal">
          <div className="modal-content">
            <h3>Edit Tweet</h3>
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              maxLength="280"
            />
            <div className="modal-actions">
              <button onClick={handleUpdate}>Save</button>
              <button onClick={() => setEditTweet(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
      {showProfile && (
        <div className="modal">
          <div className="modal-content">
            <h3>Profile</h3>
            <p>Username: {username}</p>
            <p>Tweets: {tweets.filter(t => t.username === username).length}</p>
            <p>Following: {(tweets[0]?.following || []).length}</p>
            <p>Followers: {(tweets[0]?.followers || []).length}</p>
            <input
              type="text"
              value={followUsername}
              onChange={(e) => setFollowUsername(e.target.value)}
              placeholder="Follow a user"
            />
            <button onClick={handleFollow}>Follow</button>
            <button onClick={() => setShowProfile(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Tweets;
