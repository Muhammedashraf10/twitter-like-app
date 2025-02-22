import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, signup } from './api';

function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setLoading(true);

    try {
      const data = isLogin ? await login(username, password) : await signup(username, password);
      localStorage.setItem('token', data.token);
      localStorage.setItem('username', username);
      setMessage('Success! Redirecting...');
      setTimeout(() => navigate('/tweets'), 1000);
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>{isLogin ? 'Login' : 'Signup'}</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? <span className="spinner"></span> : isLogin ? 'Login' : 'Signup'}
        </button>
      </form>
      <p className={message.includes('Success') ? 'success' : 'error'}>{message}</p>
      <button onClick={() => setIsLogin(!isLogin)} className="switch-btn">
        {isLogin ? 'Need an account? Signup' : 'Already have an account? Login'}
      </button>
    </div>
  );
}

export default Auth;
