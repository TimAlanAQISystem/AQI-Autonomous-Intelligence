"""Kill existing server on port 8777 and restart fresh."""
import subprocess, time, os

SCRIPT = r"C:\Users\signa\OneDrive\Desktop\Agent X\aqi_conversation_relay_server.py"
PYTHON = r"C:\Users\signa\OneDrive\Desktop\Agent X\.venv\Scripts\python.exe"
LOG    = r"C:\Users\signa\OneDrive\Desktop\Agent X\logs\server_fresh_start.log"
CWD    = r"C:\Users\signa\OneDrive\Desktop\Agent X"

# 1. Find PID on port 8777
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
pids = set()
for line in result.stdout.splitlines():
    if ':8777' in line and 'LISTENING' in line:
        parts = line.strip().split()
        if parts:
            try:
                pids.add(int(parts[-1]))
            except ValueError:
                pass

# 2. Kill them all
for pid in pids:
    r = subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True, text=True)
    print(f"Kill PID {pid}: {r.stdout.strip()} {r.stderr.strip()}")

time.sleep(3)

# 3. Start fresh server
with open(LOG, 'w') as log_file:
    p = subprocess.Popen(
        [PYTHON, SCRIPT],
        creationflags=0x00000008,  # DETACHED_PROCESS
        stdout=log_file,
        stderr=subprocess.STDOUT,
        cwd=CWD
    )
print(f"New server PID: {p.pid}")
