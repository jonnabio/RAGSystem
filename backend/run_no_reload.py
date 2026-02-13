"""Start the backend WITHOUT uvicorn's reload to force fresh imports."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    )
