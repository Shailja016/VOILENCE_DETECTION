/**
 * Optional: node src/seed.js — inserts sample incidents (requires MongoDB).
 */
import 'dotenv/config';
import mongoose from 'mongoose';
import { Incident } from './models/Incident.js';
import { Camera } from './models/Camera.js';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/surveillance';

const samples = [
  {
    camera_id: 'CAM-01',
    location: 'Metro Station Gate 3',
    timestamp: new Date(Date.now() - 3600000),
    violence: true,
    confidence: 0.91,
    video_url: 'C:\Users\pc\Downloads\gettyimages-670902480-640_adpp.mp4',
    detected_people: [
      { id: 'A', position: 'left', motion: 'aggressive' },
      { id: 'B', position: 'right', motion: 'defensive' },
    ],
    ai_analysis: {
      summary:
        'Two individuals were involved in a physical altercation near the turnstile. Subject A initiated contact.',
      culprit: {
        id: 'A',
        confidence: 0.87,
        reason: 'Initiated physical contact and forward aggression',
      },
      behavior: ['hitting', 'pushing'],
      risk_level: 'High',
      recommendation: 'Immediate police dispatch required',
    },
    alert_status: 'pending',
  },
  {
    camera_id: 'CAM-02',
    location: 'Parking Lot B',
    timestamp: new Date(Date.now() - 7200000),
    violence: false,
    confidence: 0.12,
    video_url: 'C:\Users\pc\Downloads\gettyimages-670902480-640_adpp.mp4',
    detected_people: [{ id: 'C', position: 'center', motion: 'neutral' }],
    ai_analysis: {
      summary: 'Routine pedestrian traffic; no violence detected.',
      culprit: { id: 'C', confidence: 0.15, reason: 'No aggressor; scene stable' },
      behavior: ['walking'],
      risk_level: 'Low',
      recommendation: 'Continue routine monitoring',
    },
    alert_status: 'resolved',
  },
];

async function run() {
  await mongoose.connect(MONGODB_URI);

  const cameraItems = [
    {
      camera_id: 'CAM-01',
      label: 'CAM-01 - North gate',
      location: 'Metro Station Gate 3',
      video_url: '/videos/gettyimages-670902480-640_adpp.mp4',
    },
    {
      camera_id: 'CAM-02',
      label: 'CAM-02 - Platform',
      location: 'Platform 2 east',
      video_url: '/videos/gettyimages-952312734-640_adpp.mp4',
    },
    {
      camera_id: 'CAM-03',
      label: 'CAM-03 - Concourse',
      location: 'Main concourse',
      video_url: '/videos/gettyimages-1078285366-640_adpp.mp4',
    },
    {
      camera_id: 'CAM-04',
      label: 'CAM-04 - Parking',
      location: 'Parking Lot B',
      video_url: '/videos/gettyimages-925063842-640_adpp.mp4',
    },
    {
      camera_id: 'CAM-05',
      label: 'CAM-05 - Retail',
      location: 'Retail wing',
      video_url: '/videos/gettyimages-820-48-640_adpp.mp4',
    },
    {
      camera_id: 'CAM-06',
      label: 'CAM-06 - Service',
      location: 'Loading dock',
      video_url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    },
  ];

  await Camera.deleteMany({});
  await Camera.insertMany(cameraItems);

  await Incident.deleteMany({});
  console.log('Seeded sample cameras and cleared old incidents.');
  await mongoose.disconnect();
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
