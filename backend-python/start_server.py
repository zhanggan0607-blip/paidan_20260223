import subprocess
import sys
import os

print("Starting backend server...")
print(f"Working directory: {os.getcwd()}")

try:
    result = subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"],
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"Server exited with code: {result.returncode}")
    else:
        print("Server started successfully!")
        
except subprocess.TimeoutExpired:
    print("Server start timed out after 30 seconds")
except Exception as e:
    print(f"Error starting server: {e}")
