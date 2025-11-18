# Raspberry Pi Frontier - Setup Guide

This guide will walk you through setting up your development environment and configuring your Raspberry Pi outposts for the Raspberry Pi Frontier learning adventure.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Raspberry Pi Configuration](#raspberry-pi-configuration)
4. [SSH Setup](#ssh-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

- **Development Computer**: Laptop or desktop running Windows, macOS, or Linux
- **Raspberry Pi Devices**: 1-3 Raspberry Pi units (3B+, 4, or 5 recommended)
- **Network**: All devices connected to the same local network
- **SD Cards**: One per Raspberry Pi (16GB+ recommended)

### Software Requirements

- **Python 3.9 or higher** installed on your development computer
- **Raspberry Pi OS** (Lite or Desktop) on each Raspberry Pi
- **Git** for version control (optional but recommended)
- **SSH Client**: Built into macOS/Linux, PuTTY for Windows

### Knowledge Prerequisites

- Basic Python programming
- Familiarity with command line/terminal
- Basic understanding of networking concepts
- Experience with text editors or IDEs

---

## Local Development Setup

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd HudsonBayOutposts

# Or download and extract the ZIP file
```

### Step 2: Create Python Virtual Environment

**On macOS/Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

**On Windows:**

```bash
python -m venv env
env\Scripts\activate
```

You should see `(env)` appear in your terminal prompt, indicating the virtual environment is active.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:
- Streamlit (web framework)
- FastAPI (API framework)
- Paramiko (SSH library)
- And all other dependencies

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite text editor
nano .env  # or vim, code, etc.
```

Update the following critical settings in `.env`:
- Raspberry Pi IP addresses
- SSH credentials
- JWT secret key (generate a secure random string)

### Step 5: Verify Installation

```bash
# Test that Streamlit is installed
streamlit --version

# Test that FastAPI dependencies are available
python -c "import fastapi; print(fastapi.__version__)"
```

---

## Raspberry Pi Configuration

### Step 1: Install Raspberry Pi OS

1. **Download Raspberry Pi Imager**: https://www.raspberrypi.org/software/
2. **Flash OS to SD Card**:
   - Insert SD card into your computer
   - Open Raspberry Pi Imager
   - Choose "Raspberry Pi OS (64-bit)" or "Raspberry Pi OS Lite"
   - Select your SD card
   - Click "Write"

3. **Enable SSH Before First Boot**:
   - After flashing, the SD card will have a `boot` partition
   - Create an empty file named `ssh` (no extension) in the boot partition
   - This enables SSH on first boot

### Step 2: Initial Boot and Network Connection

1. **Insert SD card** into Raspberry Pi
2. **Connect to network** via Ethernet or WiFi
3. **Power on** the Raspberry Pi
4. **Find the IP address**:
   - Check your router's admin panel for connected devices
   - Or use a network scanner like `nmap` or Angry IP Scanner
   - Look for devices named "raspberry" or similar

### Step 3: First SSH Connection

```bash
# Default credentials:
# Username: pi
# Password: raspberry (you'll be prompted to change this)

ssh pi@<raspberry-pi-ip-address>

# Example:
ssh pi@192.168.1.100
```

On first connection, you'll see a warning about the host key. Type `yes` to continue.

### Step 4: Initial Configuration

Once connected via SSH, run the configuration tool:

```bash
sudo raspi-config
```

Recommended settings:
1. **Change Default Password** - IMPORTANT for security
2. **Network Options** - Set up WiFi if needed
3. **Localisation Options** - Set timezone and locale
4. **Interface Options** - Ensure SSH is enabled
5. **Update** - Update the configuration tool

### Step 5: System Update

```bash
sudo apt update
sudo apt upgrade -y
```

This may take several minutes.

### Step 6: Install Python and Dependencies

```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install git sqlite3 -y

# Verify installation
python3 --version
pip3 --version
```

### Step 7: Create Project Directory on Pi

```bash
mkdir -p ~/frontier
cd ~/frontier

# Create virtual environment
python3 -m venv env
source env/bin/activate

# Install FastAPI and dependencies
pip install fastapi uvicorn[standard] pydantic psutil python-jose[cryptography] passlib[bcrypt]
```

### Step 8: Copy API Files to Raspberry Pi

From your development computer:

```bash
# Navigate to your project directory
cd HudsonBayOutposts

# Copy the API files to the Pi
scp -r raspberry_pi/ pi@192.168.1.100:~/frontier/

# Example for multiple Pis:
scp -r raspberry_pi/ pi@192.168.1.101:~/frontier/
scp -r raspberry_pi/ pi@192.168.1.102:~/frontier/
```

---

## SSH Setup

### Option 1: Password-Based Authentication (Easier)

This is already configured if you followed the steps above. You'll be prompted for the password each time you connect.

**Pros:**
- Simple to set up
- No additional configuration needed

**Cons:**
- Less secure
- Password prompts can be tedious
- Not suitable for automation

### Option 2: Key-Based Authentication (Recommended)

SSH keys provide more secure, password-less authentication.

**On your development computer:**

```bash
# Generate SSH key pair (if you don't have one)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Press Enter to accept default location (~/.ssh/id_rsa)
# Optionally set a passphrase for extra security

# Copy public key to Raspberry Pi
ssh-copy-id pi@192.168.1.100

# Test connection (should not require password)
ssh pi@192.168.1.100
```

**Update your `.env` file:**

```bash
OUTPOST_1_SSH_PASSWORD=
OUTPOST_1_SSH_KEY_PATH=~/.ssh/id_rsa
```

---

## Running the Application

### Starting the FastAPI Server on Raspberry Pi

SSH into each Raspberry Pi and start the API server:

```bash
ssh pi@192.168.1.100

cd ~/frontier
source env/bin/activate

# Run the base API server
python3 raspberry_pi/api/base_app.py

# Or use uvicorn directly for production
uvicorn raspberry_pi.api.base_app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://<pi-ip>:8000`

**To run in the background:**

```bash
# Using nohup
nohup uvicorn raspberry_pi.api.base_app:app --host 0.0.0.0 --port 8000 &

# Or create a systemd service (advanced)
```

### Starting the Streamlit Dashboard

On your development computer:

```bash
cd HudsonBayOutposts
source env/bin/activate  # env\Scripts\activate on Windows

streamlit run main.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### Verifying Everything Works

1. **Open the Streamlit dashboard** in your browser
2. **Navigate to the Outposts page**
3. **Add your Raspberry Pis** using their IP addresses
4. **Test connectivity** using the Test button
5. **Explore the API documentation** at `http://<pi-ip>:8000/docs`

---

## Troubleshooting

### Cannot SSH into Raspberry Pi

**Problem**: Connection refused or timeout

**Solutions**:
- Verify the Raspberry Pi is powered on and connected to network
- Check the IP address is correct (use `ping <ip>` to test)
- Ensure SSH is enabled: create `ssh` file in boot partition
- Check firewall settings on your router
- Try connecting via Ethernet cable instead of WiFi

### SSH Connection Works But Keeps Asking for Password

**Problem**: Key-based authentication not working

**Solutions**:
- Verify public key was copied correctly: `cat ~/.ssh/authorized_keys` on Pi
- Check permissions: `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys`
- Ensure private key path in `.env` is correct
- Try `ssh -vvv pi@<ip>` for verbose debugging output

### FastAPI Server Won't Start

**Problem**: Import errors or module not found

**Solutions**:
- Verify virtual environment is activated: `source env/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version` (must be 3.9+)
- Review error messages for specific missing modules

### Streamlit Dashboard Shows Connection Errors

**Problem**: Cannot connect to Raspberry Pi APIs

**Solutions**:
- Verify FastAPI server is running on the Pi: `curl http://<pi-ip>:8000/health`
- Check firewall settings allow HTTP traffic on port 8000
- Ensure `.env` file has correct IP addresses
- Test network connectivity: `ping <pi-ip>`
- Review API logs on the Raspberry Pi

### Virtual Environment Issues

**Problem**: Cannot activate virtual environment or import errors

**Solutions**:
- Delete and recreate the environment:
  ```bash
  rm -rf env
  python3 -m venv env
  source env/bin/activate
  pip install -r requirements.txt
  ```
- Ensure you're using the correct Python version
- On Windows, try running as Administrator

### Network Discovery Issues

**Problem**: Cannot find Raspberry Pi IP address

**Solutions**:
- Check router admin panel for connected devices
- Use network scanner: `sudo nmap -sn 192.168.1.0/24`
- Connect a monitor and keyboard to see IP directly
- Check DHCP reservation or set static IP on the Pi

### Demo Mode

If you don't have physical Raspberry Pis yet, enable Demo Mode in the Streamlit app to simulate outposts and explore the interface.

---

## Next Steps

Once everything is set up:

1. **Complete Chapter 1** - Learn SSH fundamentals
2. **Explore the API documentation** - Visit `/docs` on each Pi
3. **Experiment with remote commands** - Use the SSH module
4. **Start building your first API endpoints** - Move to Phase 2

For more help:
- Check the main [README.md](../README.md)
- Visit the Help page in the Streamlit dashboard
- Review the [troubleshooting guide](troubleshooting.md)

---

## Security Notes

⚠️ **Important Security Considerations:**

- **Change default passwords** on all Raspberry Pis
- **Use SSH keys** instead of passwords when possible
- **Keep systems updated** with `sudo apt update && sudo apt upgrade`
- **Don't expose Pis directly to the internet** - use local network only
- **Never commit `.env` files** to version control
- **Use strong, unique passwords** for all services

---

## Support

If you encounter issues not covered here:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Review error messages carefully
3. Search for similar issues online
4. Ask for help in the project discussions

Happy exploring the frontier! 🏔️
