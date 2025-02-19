from fastapi import FastAPI
from app.api import endpoints

app = FastAPI(title="COVID Digital Twin API")
app.include_router(endpoints.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
