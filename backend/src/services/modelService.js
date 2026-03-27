/**
 * Service to communicate with the Python Model Inference server.
 */
export async function callPythonModel(videoPath) {
  const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://127.0.0.1:5000/analyze-video';
  
  try {
    const response = await fetch(PYTHON_SERVICE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_path: videoPath }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Python Model Service error (${response.status}): ${errorText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error calling Python Model Service:', error.message);
    throw error;
  }
}
