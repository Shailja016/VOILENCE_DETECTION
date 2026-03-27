# Violence Detection Project

This project is structured into three main components:

1.  **base_model/**: Contains the Python-based machine learning models, training scripts, and preprocessing logic.
2.  **frontend/**: A React-based dashboard for monitoring and analyzing violence detection in real-time.
3.  **backend/**: A Node.js server that connects the frontend to the models and manages camera/incident data.

## Getting Started

### 1. Set up the Base Model
```bash
cd base_model
pip install -r requirements.txt
# To run the inference bridge server:
python inference_server.py
```

### 2. Set up the Backend
```bash
cd backend
npm install
# Configure your .env file
npm run dev
```

### 3. Set up the Frontend
```bash
cd frontend
npm install
npm run dev
```

## How it Works
- The **Frontend** communicates with the **Backend** via a proxy.
- The **Backend** calls the **Base Model** inference server (running on port 5000) whenever a violence detection scan is performed.
- If the inference server is not running, the backend falls back to mock data for demonstration purposes.

## Connection Details
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:4000`
- Model Inference: `http://localhost:5000`
