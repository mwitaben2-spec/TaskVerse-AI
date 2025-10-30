import os
from fastapi import FastAPI
from jaclang import Jac

app = FastAPI()

# Load your Jac logic safely
try:
    jac_instance = Jac()
    jac_instance.run("v1/main.jac")
    print("✅ Jac logic loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load Jac file: {e}")

@app.get("/")
def root():
    return {"message": "TaskVerse AI backend is live!"}

# --- Run server on Render-assigned port ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("v1.main:app", host="0.0.0.0", port=port)
