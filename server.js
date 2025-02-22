const express = require('express');
const path = require('path');
const app = express();

// Serve static files from the 'build' directory
app.use(express.static(path.join(__dirname, 'build')));

// Handle all routes by serving the React app's index.html
app.get('*', (req, res) => {
  console.log(`Request for: ${req.url}`);
  res.sendFile(path.join(__dirname, 'build', 'index.html'), (err) => {
    if (err) {
      console.error('Error serving index.html:', err);
      res.status(404).send('Not Found');
    }
  });
});

app.listen(3000, () => console.log('Server running on port 3000'));
