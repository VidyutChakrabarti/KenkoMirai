# Setup and Run Instructions

## Prerequisites

- Node.js (v16+)
- Python 3.9+
- Docker & Docker Compose
- Git

## Local Development

### Frontend

1. Navigate to the `frontend/` folder.
2. Install dependencies:  
   ```bash
   npm install react-leaflet leaflet framer-motion
   ```

### Backend 
 
1. Navigate to the `/backend` folder,
2. Create a virtual env 
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
3. install requirements
```bash
pip install -r requirements.txt
```
4. Run the FastAPI server 
```bash
uvicorn app.main:app --reload
```


