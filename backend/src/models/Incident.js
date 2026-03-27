import mongoose from 'mongoose';

const culpritSchema = new mongoose.Schema(
  {
    id: { type: String, default: '' },
    confidence: { type: Number, min: 0, max: 1, default: 0 },
    reason: { type: String, default: '' },
  },
  { _id: false }
);

const aiAnalysisSchema = new mongoose.Schema(
  {
    summary: { type: String, default: '' },
    culprit: { type: culpritSchema, default: () => ({}) },
    behavior: [{ type: String }],
    risk_level: {
      type: String,
      enum: ['Low', 'Medium', 'High'],
      default: 'Medium',
    },
    recommendation: { type: String, default: '' },
  },
  { _id: false }
);

const incidentSchema = new mongoose.Schema(
  {
    camera_id: { type: String, required: true, index: true },
    location: { type: String, default: '' },
    timestamp: { type: Date, default: Date.now, index: true },
    violence: { type: Boolean, default: false },
    confidence: { type: Number, min: 0, max: 1, default: 0 },
    video_url: { type: String, default: '' },
    frames: { type: [mongoose.Schema.Types.Mixed], default: [] },
    detected_people: { type: [mongoose.Schema.Types.Mixed], default: [] },
    ai_analysis: { type: aiAnalysisSchema, default: () => ({}) },
    alert_status: {
      type: String,
      enum: ['pending', 'sent', 'resolved'],
      default: 'pending',
      index: true,
    },
    status: {
      type: String,
      enum: ['processing', 'completed', 'failed'],
      default: 'completed',
    },
  },
  { timestamps: true }
);

export const Incident = mongoose.model('Incident', incidentSchema);
