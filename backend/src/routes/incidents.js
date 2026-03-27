import { Router } from 'express';
import { Incident } from '../models/Incident.js';
import { analyzeIncident } from '../services/llmService.js';

const router = Router();

function emit(io, event, payload) {
  if (io) io.emit(event, payload);
}

/**
 * POST /api/analyze-incident
 * Body: violence model output + optional video_url, camera_id, detected_people, frames
 */
router.post('/analyze-incident', async (req, res) => {
  const io = req.app.get('io');
  try {
    const body = req.body || {};
    const ai = await analyzeIncident({
      frames: body.frames,
      violence: Boolean(body.violence),
      confidence: typeof body.confidence === 'number' ? body.confidence : 0,
      location: body.location || '',
      timestamp: body.timestamp ? new Date(body.timestamp) : new Date(),
      camera_id: body.camera_id || 'unknown',
      detected_people: body.detected_people || [],
    });

    const doc = await Incident.create({
      camera_id: body.camera_id || 'unknown',
      location: body.location || '',
      timestamp: body.timestamp ? new Date(body.timestamp) : new Date(),
      violence: Boolean(body.violence),
      confidence: typeof body.confidence === 'number' ? body.confidence : 0,
      video_url: body.video_url || '',
      frames: body.frames || [],
      detected_people: body.detected_people || [],
      ai_analysis: ai,
      alert_status: body.violence ? 'pending' : 'resolved',
    });

    const populated = doc.toObject();
    emit(io, 'new_incident', { incident: populated });
    if (body.violence) {
      emit(io, 'alert_triggered', {
        incidentId: doc._id.toString(),
        risk_level: ai.risk_level,
        location: doc.location,
      });
    }

    res.status(201).json({ incident: populated, ai_analysis: ai });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message || 'Analysis failed' });
  }
});

/**
 * GET /api/incidents
 * Query: location, severity (risk_level), alert_status, limit, skip
 */
router.get('/incidents', async (req, res) => {
  try {
    const q = {};
    if (req.query.location) {
      q.location = new RegExp(req.query.location, 'i');
    }
    if (req.query.alert_status) {
      q.alert_status = req.query.alert_status;
    }
    if (req.query.severity) {
      q['ai_analysis.risk_level'] = req.query.severity;
    }
    const limit = Math.min(Number(req.query.limit) || 50, 200);
    const skip = Number(req.query.skip) || 0;

    const [items, total] = await Promise.all([
      Incident.find(q).sort({ timestamp: -1 }).skip(skip).limit(limit).lean(),
      Incident.countDocuments(q),
    ]);

    res.json({ incidents: items, total, limit, skip });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

/**
 * GET /api/incidents/:id
 */
router.get('/incidents/:id', async (req, res) => {
  try {
    const item = await Incident.findById(req.params.id).lean();
    if (!item) return res.status(404).json({ error: 'Not found' });
    res.json({ incident: item });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

/**
 * PATCH /api/incidents/:id
 * Body: { alert_status } or re-run analysis fields
 */
router.patch('/incidents/:id', async (req, res) => {
  const io = req.app.get('io');
  try {
    const updates = {};
    if (req.body.alert_status) updates.alert_status = req.body.alert_status;

    const doc = await Incident.findByIdAndUpdate(req.params.id, updates, {
      new: true,
    }).lean();
    if (!doc) return res.status(404).json({ error: 'Not found' });

    emit(io, 'incident_updated', { incident: doc });
    res.json({ incident: doc });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

/**
 * POST /api/incidents/:id/reanalyze — optional: re-run LLM on stored incident
 */
router.post('/incidents/:id/reanalyze', async (req, res) => {
  const io = req.app.get('io');
  try {
    const existing = await Incident.findById(req.params.id);
    if (!existing) return res.status(404).json({ error: 'Not found' });

    const ai = await analyzeIncident({
      frames: existing.frames,
      violence: existing.violence,
      confidence: existing.confidence,
      location: existing.location,
      timestamp: existing.timestamp,
      camera_id: existing.camera_id,
      detected_people: existing.detected_people,
    });

    existing.ai_analysis = ai;
    await existing.save();
    const obj = existing.toObject();
    emit(io, 'incident_updated', { incident: obj });
    res.json({ incident: obj });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

export default router;
