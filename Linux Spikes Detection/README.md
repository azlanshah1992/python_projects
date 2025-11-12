# Load Spike Detector and Diagnostics System

**This project is a small, standalone system designed to continuously monitor the 5-minute load average on a Linux server (like an EC2 instance). When the load exceeds a predefined threshold, it automatically executes a diagnostic script to capture critical system state information (CPU usage, memory, running processes) and archives it.**

**The system also includes a simple Python web server and dashboard for real-time log viewing and browser-based downloading of the captured diagnostic archives, bypassing the need for complex SCP/SFTP configuration.**

## Key Features

**Continuous Monitoring: Uses a crontab job to check the server load every 5 minutes.**

**Automated Diagnostics: Captures system information (top, ps aux, free -h) when a load spike is detected.**

**Web Dashboard: Real-time log visualization via a web browser (http://<IP>:8080).**

---

## Project Files

File: spike_detector.py
Purpose: The core Python script that checks the load, triggers diagnostics, and creates archives.
Location: /home/ec2-user/
--
File: dashboard_server.py
Purpose: The Python web server script that hosts the dashboard and manages file downloads.
Location: /home/ec2-user/
--
File: spike_detector.log
Purpose: The primary log file where all execution details (load checks, spikes) are recorded.
Location: /home/ec2-user/
--
File/Folder: diagnostics/
Purpose: Directory where all captured .tar.gz archive files are stored.
Location: /home/ec2-user/diagnostics/

---

## Setup and Installation

These steps assume you are connected to your Linux server (e.g., EC2 instance) via SSH.

**1. Prerequisite: Install Python and Utilities**

Ensure you have Python 3 and the necessary diagnostic utilities installed.

**Update package lists**
	sudo yum update -y

**Install Python 3 (or ensure it's available) and essential tools**
	sudo yum install python3 sysstat procps-ng -y

**Create the diagnostics directory**
	mkdir -p /home/ec2-user/diagnostics


**2. Configure Crontab for Monitoring**

The core script must run continuously. We recommend running it every 5 minutes.

Open the crontab editor (Vim or Nano):

	crontab -e

Add the following line to the end of the file, replacing <PATH_TO_PYTHON> with your absolute Python path (usually /usr/bin/python3 or similar):

	*/5 * * * * <PATH_TO_PYTHON> /home/ec2-user/spike_detector.py >> /home/ec2-user/spike_detector.log 2>&1


Save and exit (in vim, press escape sequence, then :wq, then Enter).

**3. Start the Web Dashboard Server**

The web server needs to run continuously in the background to serve the dashboard and file downloads.

Use nohup and & to run the server in the background and keep it running even if you close your SSH session:
for example:
	nohup python3 /home/ec2-user/dashboard_server.py &

Check the server status:

	tail -f nohup.out

You should see the output confirming the server started on port 8080.


## Accessing the Dashboard

The server exposes two URLs:

1. Main Dashboard

View the real-time log history and system summary.

	http://<Your-EC2-Public-IP>:8080/


## Stopping the Web Server

If you need to stop the dashboard server for maintenance or updates:

Find the process ID (PID) of the running dashboard_server.py script:

	ps aux | grep dashboard_server.py


Identify the PID (the number in the second column) and stop the process:

	kill <PID_NUMBER>


📝 Configuration (In spike_detector.py)

You can modify the following variables inside spike_detector.py to customize the system's behavior:

Variable

Default Value

Description

LOAD_THRESHOLD

2.0

The 5-minute load average value that triggers a diagnostic capture.

DIAGNOSTICS_DIR

/home/ec2-user/diagnostics

The directory where diagnostic archives are saved.

LOG_FILE_PATH

/home/ec2-user/spike_detector.log

The file used for logging all execution attempts.