from fastapi import FastAPI
import subprocess
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "TaskVerse AI backend is live!"}

@app.post("/run_jac")
def run_jac():
    """Executes Jac logic if main.jac exists."""
    jac_file = os.path.join(os.path.dirname(__file__), "main.jac")
    if not os.path.exists(jac_file):
        return {"status": "error", "error": "main.jac not found"}

    try:
        # Run Jac file safely and capture output
        result = subprocess.run(
            ["jac", "run", jac_file],
            capture_output=True,
            text=True
        )
        return {"status": "success", "output": result.stdout or result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}
