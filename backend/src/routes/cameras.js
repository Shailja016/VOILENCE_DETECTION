import { Router } from 'express';
import { Camera } from '../models/Camera.js';
import { Incident } from '../models/Incident.js';
import { analyzeIncident } from '../services/llmService.js';
import { callPythonModel } from '../services/modelService.js';

const router = Router();

function emit(io, event, payload) {
  if (io) io.emit(event, payload);
}

// GET /api/cameras
router.get('/cameras', async (_req, res) => {
  try {
    const items = await Camera.find({ enabled: true }).sort({ camera_id: 1 }).lean();
    res.json({ cameras: items });
  } catch (e) {
    res.status(500).json({ error: e.message || 'Failed to load cameras' });
  }
});

// POST /api/cameras/:id/scan
// Triggers: vision model -> LLM culprit + summary -> stores an Incident -> emits sockets.
router.post('/cameras/:id/scan', async (req, res) => {
  const io = req.app.get('io');
  let incidentDoc = null;
  
  try {
    const camera = await Camera.findOne({ camera_id: req.params.id, enabled: true }).lean();
    if (!camera) return res.status(404).json({ error: 'Camera not found' });

    // 0. Create a placeholder incident if we want to show 'processing'
    incidentDoc = await Incident.create({
      camera_id: camera.camera_id,
      location: camera.location,
      timestamp: new Date(),
      status: 'processing',
      video_url: camera.video_url || '',
    });
    emit(io, 'new_incident', { incident: incidentDoc.toObject() });

    // 1. Call Python Model Service
    const vision = await callPythonModel(camera.video_url);

    // 2. Call LLM Service for deeper analysis
    const ai = await analyzeIncident({
      frames: vision.frames || [], 
      violence: vision.violence,
      confidence: vision.confidence,
      location: camera.location,
      timestamp: new Date(),
      camera_id: camera.camera_id,
      detected_people: vision.detected_people,
    });

    // 3. Update Incident in MongoDB
    incidentDoc.violence = vision.violence;
    incidentDoc.confidence = vision.confidence;
    incidentDoc.frames = vision.frames || [];
    incidentDoc.detected_people = vision.detected_people || [];
    incidentDoc.ai_analysis = ai;
    incidentDoc.alert_status = vision.violence ? 'pending' : 'resolved';
    incidentDoc.status = 'completed';
    await incidentDoc.save();

    const populated = incidentDoc.toObject();
    
    // 4. Emit update to Frontend via Socket.io
    emit(io, 'incident_updated', { incident: populated });
    
    if (vision.violence) {
      emit(io, 'alert_triggered', {
        incidentId: incidentDoc._id.toString(),
        risk_level: ai.risk_level,
        location: incidentDoc.location,
      });
    }

    res.status(201).json({ incident: populated, ai_analysis: ai });
  } catch (e) {
    console.error('Scan error:', e);
    
    if (incidentDoc) {
      incidentDoc.status = 'failed';
      await incidentDoc.save();
      emit(io, 'incident_updated', { incident: incidentDoc.toObject() });
    }
    
    res.status(500).json({ error: e.message || 'Scan failed' });
  }
});

export default router;

