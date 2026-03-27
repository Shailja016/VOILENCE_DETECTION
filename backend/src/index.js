import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import mongoose from 'mongoose';
import incidentRoutes from './routes/incidents.js';
import cameraRoutes from './routes/cameras.js';
import { getLlmRuntimeInfo } from './services/llm/status.js';

const PORT = Number(process.env.PORT) || 4000;
const CLIENT_ORIGIN = process.env.CLIENT_ORIGIN || '*';
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/surveillance';

const app = express();
const httpServer = createServer(app);

const io = new Server(httpServer, {
  cors: {
    origin: CLIENT_ORIGIN === '*' ? true : CLIENT_ORIGIN.split(',').map((s) => s.trim()),
    methods: ['GET', 'POST', 'PATCH'],
  },
});

app.set('io', io);
app.use(
  cors({
    origin: CLIENT_ORIGIN === '*' ? true : CLIENT_ORIGIN.split(',').map((s) => s.trim()),
  })
);
app.use(express.json({ limit: '15mb' }));

app.get('/api/health', (_req, res) => {
  res.json({
    ok: true,
    mongo: mongoose.connection.readyState === 1,
    llm: getLlmRuntimeInfo(),
  });
});

app.use('/api', incidentRoutes);
app.use('/api', cameraRoutes);

io.on('connection', (socket) => {
  socket.emit('connected', { socketId: socket.id });
});

async function main() {
  await mongoose.connect(MONGODB_URI);
  console.log('MongoDB connected');

  httpServer.listen(PORT, () => {
    console.log(`API + Socket.io listening on http://localhost:${PORT}`);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
