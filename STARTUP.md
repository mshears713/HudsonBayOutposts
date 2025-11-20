# Hudson Bay Expedition Console - Windows Startup Guide

**Complete step-by-step instructions for beginners on Windows**

---

## Prerequisites Installation

### 1. Install Python 3.10+

1. Go to https://www.python.org/downloads/
2. Download Python 3.10 or newer (3.11 recommended)
3. **IMPORTANT:** During installation, check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   - Open Command Prompt (press `Win + R`, type `cmd`, press Enter)
   - Type: `python --version`
   - You should see: `Python 3.11.x` (or similar)

### 2. Install PostgreSQL

1. Go to https://www.postgresql.org/download/windows/
2. Download and run the installer
3. During installation:
   - Remember the password you set for user `postgres`
   - Default port: `5432` (keep this)
   - Install pgAdmin 4 (the GUI tool)
4. Verify installation:
   - Open pgAdmin 4 from Start menu
   - You should see the PostgreSQL server

### 3. Install Node.js

1. Go to https://nodejs.org/
2. Download the LTS version (left button)
3. Run the installer (accept all defaults)
4. Verify installation:
   - Open Command Prompt
   - Type: `node --version`
   - You should see: `v18.x.x` or similar
   - Type: `npm --version`
   - You should see: `9.x.x` or similar

### 4. Install Git (Optional but Recommended)

1. Go to https://git-scm.com/download/win
2. Download and install Git for Windows
3. Accept all defaults during installation

---

## Project Setup

### Step 1: Get the Project Files

**Option A: If you have Git installed:**
```cmd
cd Desktop
git clone <repository-url>
cd HudsonBayOutposts
```

**Option B: If you downloaded a ZIP:**
1. Extract the ZIP file to your Desktop
2. Open Command Prompt
3. Navigate to the folder:
```cmd
cd Desktop\HudsonBayOutposts
```

### Step 2: Set Up the Database

1. **Open pgAdmin 4** from the Start menu

2. **Connect to PostgreSQL:**
   - Click on "Servers" → "PostgreSQL"
   - Enter the password you set during installation

3. **Create the database:**
   - Right-click on "Databases"
   - Select "Create" → "Database"
   - Database name: `hudsonbay`
   - Owner: `postgres`
   - Click "Save"

4. **Create a user (optional but recommended):**
   - Right-click on "Login/Group Roles"
   - Select "Create" → "Login/Group Role"
   - General tab → Name: `hudsonbay`
   - Definition tab → Password: `hudsonbay`
   - Privileges tab → Check "Can login?" and "Superuser"
   - Click "Save"

### Step 3: Set Up the Backend

1. **Open Command Prompt** and navigate to the project:
```cmd
cd Desktop\HudsonBayOutposts\backend
```

2. **Create a Python virtual environment:**
```cmd
python -m venv .venv
```

3. **Activate the virtual environment:**
```cmd
.venv\Scripts\activate
```
*You should see `(.venv)` at the start of your command line*

4. **Install Python dependencies:**
```cmd
pip install -r requirements.txt
```
*This takes 1-2 minutes*

5. **Create environment configuration:**
   - Open Notepad
   - Copy this text:
```
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/hudsonbay
CORS_ORIGINS=http://localhost:3000
SQL_ECHO=false
LOG_LEVEL=INFO
```
   - Replace `YOUR_PASSWORD` with your PostgreSQL password
   - Save as `.env` in the `backend` folder
   - **Important:** Save as "All Files" type, not "Text Document"

6. **Set up the database tables:**
```cmd
alembic upgrade head
```

7. **Add sample data:**
```cmd
python seed_data.py
```
*You should see: "✅ Database seeding complete!"*

8. **Start the backend server:**
```cmd
uvicorn main:app --reload
```

**✅ Backend is running!**
- You should see: "Uvicorn running on http://127.0.0.1:8000"
- Open browser to http://localhost:8000/docs to see the API
- **KEEP THIS COMMAND PROMPT WINDOW OPEN**

### Step 4: Set Up the Frontend

1. **Open a NEW Command Prompt window** (keep the backend running)

2. **Navigate to frontend folder:**
```cmd
cd Desktop\HudsonBayOutposts\frontend
```

3. **Install Node.js dependencies:**
```cmd
npm install
```
*This takes 2-3 minutes*

4. **Create environment configuration:**
   - Open Notepad
   - Copy this text:
```
REACT_APP_API_URL=http://localhost:8000
```
   - Save as `.env` in the `frontend` folder
   - **Important:** Save as "All Files" type, not "Text Document"

5. **Start the frontend server:**
```cmd
npm start
```
*This takes 30-60 seconds*

**✅ Frontend is running!**
- Browser should open automatically to http://localhost:3000
- If not, open browser and go to http://localhost:3000
- **KEEP THIS COMMAND PROMPT WINDOW OPEN TOO**

---

## Using the Application

### You Now Have 2 Command Prompt Windows Open:

1. **Backend window** - Running `uvicorn` (port 8000)
2. **Frontend window** - Running `npm start` (port 3000)

### Explore the Application:

1. **Home Page:** http://localhost:3000
   - Overview of the expedition console

2. **Outposts:** http://localhost:3000/outposts
   - View all 4 sample outposts
   - See their locations and details

3. **Expedition Logs:** http://localhost:3000/logs
   - View sensor readings and status updates
   - Color-coded by event type

4. **API Documentation:** http://localhost:8000/docs
   - Interactive API testing interface
   - Try making API calls directly

---

## Stopping the Application

### To Stop the Servers:

1. Go to each Command Prompt window
2. Press `Ctrl + C`
3. Type `Y` if asked to terminate
4. Close the Command Prompt windows

---

## Restarting the Application Later

### Backend:
```cmd
cd Desktop\HudsonBayOutposts\backend
.venv\Scripts\activate
uvicorn main:app --reload
```

### Frontend (in a separate Command Prompt):
```cmd
cd Desktop\HudsonBayOutposts\frontend
npm start
```

---

## Troubleshooting

### "Python is not recognized..."
- Reinstall Python and check "Add Python to PATH"
- Or restart your computer after installing

### "npm is not recognized..."
- Reinstall Node.js
- Restart your computer after installing

### "Could not connect to database"
- Make sure PostgreSQL is running (check pgAdmin 4)
- Verify your password in the `.env` file
- Check that database `hudsonbay` exists in pgAdmin

### "Port 8000 already in use"
- Another program is using that port
- Find and close that program, or change the port:
```cmd
uvicorn main:app --reload --port 8001
```
- Update `.env` in frontend: `REACT_APP_API_URL=http://localhost:8001`

### "Port 3000 already in use"
- Another program is using that port
- The terminal will ask if you want to use a different port (press `Y`)

### Frontend shows "Failed to fetch"
- Make sure backend is running on port 8000
- Check http://localhost:8000/health in your browser
- Make sure `.env` file exists in frontend folder

### Database errors when running seed_data.py
- Make sure you ran `alembic upgrade head` first
- Drop and recreate the database in pgAdmin if needed
- Run migrations again

---

## What You're Running

### Backend (Python/FastAPI):
- **Location:** `backend/` folder
- **Purpose:** REST API server providing data
- **Port:** 8000
- **Files:**
  - `main.py` - API endpoints
  - `models.py` - Database structure
  - `database.py` - Database connection

### Frontend (React/TypeScript):
- **Location:** `frontend/` folder
- **Purpose:** User interface in the browser
- **Port:** 3000
- **Files:**
  - `src/App.tsx` - Main app component
  - `src/pages/` - Page components
  - `src/components/` - Reusable UI components

### Database (PostgreSQL):
- **Purpose:** Stores outpost and log data
- **Port:** 5432
- **Management:** pgAdmin 4

---

## Next Steps

1. **Explore the API:**
   - Go to http://localhost:8000/docs
   - Try the "GET /outposts" endpoint
   - Try creating a log entry

2. **Modify the data:**
   - Edit `backend/seed_data.py`
   - Add more outposts
   - Run `python seed_data.py` again

3. **Customize the frontend:**
   - Edit files in `frontend/src/`
   - Changes appear automatically (hot reload)

4. **Learn more:**
   - Read `README2.md` for architecture
   - Read `backend/README.md` for API details
   - Read `frontend/README.md` for UI development

---

## File Locations Reference

```
Desktop\HudsonBayOutposts\
├── backend\
│   ├── .venv\                 (Python virtual environment)
│   ├── .env                   (Your database password - CREATE THIS)
│   ├── main.py                (API server)
│   ├── seed_data.py           (Sample data script)
│   └── requirements.txt       (Python packages list)
│
├── frontend\
│   ├── node_modules\          (Node.js packages)
│   ├── .env                   (API URL - CREATE THIS)
│   ├── src\                   (Source code)
│   └── package.json           (Node.js packages list)
│
└── README2.md                 (Main documentation)
```

---

## Getting Help

### Check These First:
1. Are both servers running? (You should have 2 Command Prompts open)
2. Can you access http://localhost:8000/docs?
3. Can you access http://localhost:3000?
4. Is PostgreSQL running? (Check pgAdmin 4)

### Common Commands:

**Check if Python is installed:**
```cmd
python --version
```

**Check if Node.js is installed:**
```cmd
node --version
npm --version
```

**Check if PostgreSQL is running:**
- Open pgAdmin 4
- Look for the server to be connected (green icon)

### Still Having Issues?

1. **Try restarting your computer**
2. **Make sure all prerequisites are installed**
3. **Check that `.env` files are created correctly**
4. **Verify PostgreSQL database `hudsonbay` exists**

---

**🎉 You're all set! Enjoy exploring the Hudson Bay Expedition Console!**
