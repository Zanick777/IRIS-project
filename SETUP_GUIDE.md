# IRIS Setup Guide - GitHub to Local Deployment

This guide explains how to set up IRIS on a new machine after cloning from GitHub.

## 🔒 Security Overview

IRIS keeps your personal information secure by:
- ✅ Using environment variables for all personal data
- ✅ Excluding `.env` from Git via `.gitignore`
- ✅ Providing `.env.example` as a template
- ✅ Never hardcoding secrets in the codebase

## 📋 What's Protected

The following information is stored locally and never committed to GitHub:

1. **Personal Information**
   - Your name (for personalized greetings)

2. **Location Data**
   - City names
   - GPS coordinates (latitude/longitude)

3. **Server Configuration**
   - Server host and port settings
   - Update intervals
   - Debug settings

## 🚀 Setting Up on a New Machine

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/iris-dashboard.git
cd iris-dashboard
```

### Step 2: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

Or manually:
```bash
pip3 install aiohttp python-socketio python-dotenv
```

### Step 3: Create Your Environment File

Copy the example environment file:
```bash
cp .env.example .env
```

### Step 4: Customize Your Settings

Edit `.env` with your personal information:

```bash
nano .env  # or use vim, code, etc.
```

**Required Settings:**

```env
# Your name for personalized greetings
USER_NAME=YourName

# Primary location (e.g., your home city)
PRIMARY_CITY=YourCity
PRIMARY_LATITUDE=00.0000
PRIMARY_LONGITUDE=-00.0000

# Secondary location (e.g., work city, vacation home)
SECONDARY_CITY=AnotherCity
SECONDARY_LATITUDE=00.0000
SECONDARY_LONGITUDE=-00.0000
```

**Finding Your Coordinates:**
1. Go to [LatLong.net](https://www.latlong.net/)
2. Enter your city name
3. Copy the latitude and longitude values
4. Paste them into your `.env` file

### Step 5: Start the Server

```bash
./start_iris.sh
```

Or manually:
```bash
python3 dashboard_server.py
```

### Step 6: Access Your Dashboard

Open your browser to: **http://localhost:8080**

You should see:
- Your personalized greeting with your name
- Weather for your configured locations
- Real-time XRP prices
- Latest news feed
- Tech news page (click "🚀 Tech News" button)

## 🔄 When You Make Changes

### Adding Your Changes to Git

Before committing:
1. Verify `.env` is not being tracked:
   ```bash
   git status
   ```
   You should NOT see `.env` in the list

2. Add and commit your changes:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```

### Files That WILL Be Committed

✅ Source code (`.py`, `.html`, `.sh`)
✅ Documentation (`.md`, `.txt`)
✅ Configuration templates (`.env.example`)
✅ `.gitignore` file

### Files That WON'T Be Committed (Protected)

❌ `.env` - Your personal settings
❌ `*.log` - Server logs
❌ `__pycache__/` - Python cache
❌ `.vscode/` - Editor settings
❌ Any files listed in `.gitignore`

## 🛠️ Troubleshooting

### "I don't see my name in the greeting"

1. Check that `.env` exists: `ls -la .env`
2. Verify `USER_NAME` is set in `.env`: `cat .env | grep USER_NAME`
3. Restart the server to reload environment variables

### "Weather shows wrong location"

1. Verify your coordinates in `.env`
2. Check that coordinates are in decimal format (e.g., `32.8140`, not degrees/minutes/seconds)
3. Restart the server

### "python-dotenv not found"

Install the missing dependency:
```bash
pip3 install python-dotenv
```

## 📁 File Structure

```
iris-dashboard/
├── .env                    # ❌ Your local settings (NOT in Git)
├── .env.example           # ✅ Template (IN Git)
├── .gitignore             # ✅ Exclusion rules (IN Git)
├── dashboard_server.py    # ✅ Backend server (IN Git)
├── Dashboard.html         # ✅ Main dashboard (IN Git)
├── TechNews.html          # ✅ Tech news page (IN Git)
├── requirements.txt       # ✅ Dependencies (IN Git)
├── README.md              # ✅ Documentation (IN Git)
└── start_iris.sh          # ✅ Startup script (IN Git)
```

## 🔐 Security Best Practices

1. **Never commit `.env`** - It's already in `.gitignore`, but double-check!
2. **Use `.env.example`** - Update this template when adding new variables
3. **Don't share coordinates publicly** - They reveal your exact location
4. **Rotate API keys** - If you add paid APIs later, rotate keys periodically

## 📝 Example .env File

Here's what your `.env` should look like:

```env
# IRIS - Intelligent Reasoning and Interface System
# Local Environment Configuration

# Personal Information
USER_NAME=Zack

# Location Settings
PRIMARY_CITY=Irving
PRIMARY_LATITUDE=32.8140
PRIMARY_LONGITUDE=-96.9489

SECONDARY_CITY=Lewisville
SECONDARY_LATITUDE=33.0462
SECONDARY_LONGITUDE=-96.9942

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
UPDATE_INTERVAL=300
DEBUG_MODE=false
```

## ✅ Verification Checklist

Before pushing to GitHub:
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` is up to date
- [ ] No personal data in source code
- [ ] `git status` shows no `.env` file
- [ ] README documents all environment variables

After cloning on new machine:
- [ ] Created `.env` from `.env.example`
- [ ] Filled in all personal settings
- [ ] Installed all dependencies
- [ ] Server starts without errors
- [ ] Dashboard shows personalized data

---

**Ready to deploy?** Follow the steps above and your IRIS dashboard will be running with your personal settings in minutes! 🚀
