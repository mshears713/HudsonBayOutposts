# Raspberry Pi Frontier - Quick Start Guide

Get up and running with Raspberry Pi Frontier in under 30 minutes!

## Prerequisites

- Python 3.9+ installed
- 1-3 Raspberry Pis with SSH enabled (or use Demo Mode)
- All devices on the same network

## 5-Minute Local Setup

```bash
# 1. Navigate to project directory
cd HudsonBayOutposts

# 2. Create virtual environment
python3 -m venv env

# 3. Activate virtual environment
source env/bin/activate  # macOS/Linux
# OR
env\Scripts\activate     # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your Pi IP addresses

# 6. Start the dashboard
streamlit run main.py
```

Your dashboard will open at http://localhost:8501

## Using Demo Mode (No Hardware Needed)

1. Start the Streamlit app: `streamlit run main.py`
2. Check "Demo Mode" on the Home page
3. Add virtual outposts on the Outposts page
4. Explore the interface!

## With Physical Raspberry Pis

### Raspberry Pi Setup (15 minutes per Pi)

```bash
# 1. SSH into your Pi
ssh pi@<raspberry-pi-ip>

# 2. Update system
sudo apt update && sudo apt upgrade -y

# 3. Install dependencies
sudo apt install python3 python3-pip python3-venv -y

# 4. Create project directory
mkdir -p ~/frontier
cd ~/frontier
python3 -m venv env
source env/bin/activate

# 5. Install API dependencies
pip install fastapi uvicorn[standard] pydantic psutil
```

### Deploy API to Pi

From your development computer:

```bash
# Copy API files to Pi
scp -r raspberry_pi/ pi@<raspberry-pi-ip>:~/frontier/
```

### Start API Server on Pi

```bash
# SSH into Pi
ssh pi@<raspberry-pi-ip>

# Navigate and activate environment
cd ~/frontier
source env/bin/activate

# Start the API
python3 raspberry_pi/api/base_app.py
```

API will be available at http://&lt;pi-ip&gt;:8000

### Connect Dashboard to Your Pis

1. Open Streamlit dashboard
2. Go to "Outposts" page
3. Click "Add New Outpost"
4. Enter your Pi details:
   - Name: "Fort William"
   - Type: "fishing"
   - IP: Your Pi's IP address
   - Port: 8000
5. Click "Add Outpost"

## Verify Everything Works

1. **Test API**: Visit http://&lt;pi-ip&gt;:8000/docs
2. **Test SSH**: Try connecting from dashboard
3. **Explore**: Navigate through chapters

## Next Steps

- **Chapter 1**: Learn SSH fundamentals
- **Read Docs**: Check `/docs/setup_guide.md` for detailed info
- **Experiment**: Try remote commands via SSH module

## Common Issues

### Cannot find Raspberry Pi IP?

```bash
# Scan your network
sudo nmap -sn 192.168.1.0/24

# Or check your router's admin panel
```

### SSH connection refused?

- Ensure SSH is enabled on Pi
- Create empty file named `ssh` in boot partition
- Verify network connectivity with `ping <pi-ip>`

### Import errors?

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify Python version
python3 --version  # Must be 3.9+
```

### Port already in use?

```bash
# Change port in .env file
STREAMLIT_SERVER_PORT=8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9
```

## Getting Help

- Full setup guide: `/docs/setup_guide.md`
- Troubleshooting: `/docs/troubleshooting.md`
- Help page in dashboard: Click "Help" in sidebar

Happy exploring! 🏔️
