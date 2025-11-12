import psutil
import subprocess
import os
import time
import tarfile
from datetime import datetime, timedelta

# --- Configuration Variables ---
# Define the threshold for the 5-minute load average.
# Load average is the average number of processes waiting for CPU time.
# A value of 8.0 is high for an 8-core system, but adjust based on your server's core count.
LOAD_THRESHOLD = 2.0

# Directory to store the diagnostic archives. MUST exist on the target system.
DIAGNOSTICS_DIR = "/tmp/system_diagnostics" # Use /var/log/diagnostics in a real setup (requires root)

# Retention policy: remove archives older than this many days.
RETENTION_DAYS = 7

# List of critical Linux commands to execute during a spike.
# The output will be saved to separate files inside the archive.
DIAGNOSTIC_COMMANDS = {
    "top_snapshot": "top -b -n 1", # Non-interactive, single snapshot of processes
    "vmstat_snapshot": "vmstat -s", # Memory statistics
    "netstat_connections": "netstat -tulnp", # Network listening ports and PIDs
    "disk_usage": "df -h", # Disk space usage
}

# --- Utility Functions ---

def log_message(message):
    """Prints a timestamped message to the console for cron logging."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def check_load_threshold():
    """
    Checks the current 5-minute load average using psutil.
    Returns True if the load exceeds the defined threshold.
    """
    try:
        # psutil returns (1-min, 5-min, 15-min) load averages
        load_avg_5min = psutil.getloadavg()[1]
        log_message(f"Current 5-minute Load Average: {load_avg_5min:.2f} (Threshold: {LOAD_THRESHOLD:.2f})")
        return load_avg_5min >= LOAD_THRESHOLD
    except Exception as e:
        log_message(f"ERROR: Failed to retrieve load average: {e}")
        return False

def capture_diagnostics():
    """Executes defined Linux commands and saves output to temporary files."""
    log_message("Threshold exceeded. Starting diagnostic data capture...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_capture_dir = os.path.join(DIAGNOSTICS_DIR, f"capture_{timestamp}")

    # 1. Ensure the temporary directory is created
    os.makedirs(temp_capture_dir, exist_ok=True)

    # 2. Execute each diagnostic command
    for filename, command in DIAGNOSTIC_COMMANDS.items():
        output_filepath = os.path.join(temp_capture_dir, f"{filename}.txt")
        try:
            # Use shell=True for complex commands (like netstat) or pipes, but handle security risks
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True, # Raise error if command fails
                timeout=10 # Timeout in case command hangs
            )
            with open(output_filepath, 'w') as f:
                f.write(f"--- Command: {command} ---\n")
                f.write(result.stdout)
            log_message(f"Successfully captured {filename}")
        except subprocess.CalledProcessError as e:
            log_message(f"WARNING: Command '{command}' failed (Exit Code {e.returncode}). Stderr: {e.stderr.strip()}")
        except subprocess.TimeoutExpired:
            log_message(f"WARNING: Command '{command}' timed out.")
        except Exception as e:
            log_message(f"ERROR executing command: {e}")

    # 3. Create the archive and clean up the temporary folder
    archive_name = f"spike_diag_{timestamp}.tar.gz"
    archive_path = os.path.join(DIAGNOSTICS_DIR, archive_name)

    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(temp_capture_dir, arcname=os.path.basename(temp_capture_dir))
        log_message(f"Successfully created archive: {archive_name}")
    except Exception as e:
        log_message(f"ERROR: Failed to create archive: {e}")
    finally:
        # Clean up the temporary directory containing unarchived files
        subprocess.run(['rm', '-rf', temp_capture_dir], check=False)

    return archive_path

def cleanup_old_archives():
    """Removes archived files older than the defined retention period."""
    log_message("Starting archive cleanup...")

    if not os.path.exists(DIAGNOSTICS_DIR):
        log_message("Diagnostics directory does not exist. Skipping cleanup.")
        return

    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)

    files_deleted = 0
    for filename in os.listdir(DIAGNOSTICS_DIR):
        filepath = os.path.join(DIAGNOSTICS_DIR, filename)

        # Only process files (not sub-directories)
        if os.path.isfile(filepath):
            # Get file modification time and convert to datetime object
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))

            if file_mod_time < cutoff_date:
                try:
                    os.remove(filepath)
                    log_message(f"Cleaned up old archive: {filename}")
                    files_deleted += 1
                except OSError as e:
                    log_message(f"ERROR: Could not delete {filename}: {e}")

    log_message(f"Cleanup complete. Total files deleted: {files_deleted}")

# --- Main Execution Logic ---

def main():
    """The main logic executed by the cron job."""

    # 1. Ensure the diagnostics directory exists
    os.makedirs(DIAGNOSTICS_DIR, exist_ok=True)

    # 2. Check the load threshold
    if check_load_threshold():
        # 3. If load is too high, capture diagnostics
        archive_path = capture_diagnostics()
        # Optionally, add code here to email the archive path or push a notification
    else:
        log_message("Load is within acceptable limits. No action taken.")

    # 4. Always run the cleanup to prevent disk filling
    cleanup_old_archives()

if __name__ == "__main__":
    main()
