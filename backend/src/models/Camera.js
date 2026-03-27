import mongoose from 'mongoose';

const cameraSchema = new mongoose.Schema(
  {
    camera_id: { type: String, required: true, unique: true, index: true },
    label: { type: String, default: '' },
    location: { type: String, default: '' },
    video_url: { type: String, default: '' },
    /**
     * Demo switch: when true, the backend mock-vision detector will flag violence.
     * Replace this with your real CNN/LSTM/Transformer violence detector later.
     */
    mock_violence: { type: Boolean, default: false },
    enabled: { type: Boolean, default: true },
  },
  { timestamps: true }
);

export const Camera = mongoose.model('Camera', cameraSchema);

