const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let lastState = null;

function broadcast(obj) {
  const raw = JSON.stringify(obj);
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) client.send(raw);
  });
}

// HTTP endpoint for external app to POST state to
// Expected payload: { darkened: [true, true, false, ...] }
app.post('/update', (req, res) => {
  const body = req.body;
  if (!body || !Array.isArray(body.darkened)) {
    return res.status(400).json({ error: 'Expected { darkened: [...] }' });
  }
  lastState = body;
  broadcast(body);
  res.json({ ok: true });
});

// Serve static files (optional) so you can open http://localhost:3000/
app.use(express.static(__dirname));

wss.on('connection', ws => {
  console.log('WS client connected');
  if (lastState) ws.send(JSON.stringify(lastState));
  ws.on('close', () => console.log('WS client disconnected'));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', () => process.exit());
