/**
 * Violence detector.
 * Connects to the Python inference server running at http://localhost:5000/predict.
 * Returns: { violence: boolean, confidence: number, detected_people: [{id, position, motion}] }
 */
export async function detectViolenceForCamera(camera) {
  try {
    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        camera_id: camera.camera_id, 
        video_url: camera.video_url,
        mock_violence: camera.mock_violence 
      }),
    });

    if (!response.ok) {
      throw new Error(`Inference server responded with ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.warn('Inference server not available. Falling back to mock data.', error.message);
    
    // Fallback to mock data if inference server is not available
    const baseConfidence = camera.mock_violence ? 0.86 : 0.16;
    const confidence =
      camera.mock_violence
        ? Math.max(0.6, Math.min(0.98, baseConfidence + (Math.random() - 0.5) * 0.12))
        : Math.max(0.02, Math.min(0.45, baseConfidence + (Math.random() - 0.5) * 0.10));

    if (camera.mock_violence) {
      return {
        violence: true,
        confidence,
        detected_people: [
          { id: 'A', position: 'left', motion: 'aggressive' },
          { id: 'B', position: 'right', motion: 'defensive' },
        ],
      };
    }

    return {
      violence: false,
      confidence,
      detected_people: [{ id: 'C', position: 'center', motion: 'neutral' }],
    };
  }
}

