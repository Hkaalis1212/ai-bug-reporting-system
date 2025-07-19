# 💻 How to Run Your Trucking Tool Locally

## For Windows Users:

### 1. Install Python
- Go to [python.org](https://python.org)
- Download Python 3.8 or newer
- **Important:** Check "Add Python to PATH" during installation

### 2. Download Your Files
- Download all files from your workspace to a folder like `C:\FleetOptimize\`
- Make sure you have:
  - `trucking_optimization_audit.py`
  - `requirements.txt`
  - `run_client_audit.py`

### 3. Open Command Prompt
- Press `Windows + R`
- Type `cmd` and press Enter
- Navigate to your folder: `cd C:\FleetOptimize\`

### 4. Install Dependencies
```cmd
pip install -r requirements.txt
```

### 5. Run the Tool
```cmd
python trucking_optimization_audit.py
```

## For Mac Users:

### 1. Install Python (if not already installed)
- Open Terminal (Applications → Utilities → Terminal)
- Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Install Python: `brew install python`

### 2. Download Your Files
- Create folder: `mkdir ~/FleetOptimize`
- Put all your files in `~/FleetOptimize/`

### 3. Open Terminal
- Navigate to folder: `cd ~/FleetOptimize`

### 4. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 5. Run the Tool
```bash
python3 trucking_optimization_audit.py
```

## For Linux Users:

### 1. Install Python and pip
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Download Files
```bash
mkdir ~/FleetOptimize
cd ~/FleetOptimize
# Copy your files here
```

### 3. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 4. Run the Tool
```bash
python3 trucking_optimization_audit.py
```

## 🎯 What You'll See:

All platforms will show:
```
📊 Creating sample trucking data...
✅ Sample data created: sample_trucking_data.csv
🚛 Starting Trucking Fleet Optimization Audit...
==================================================
✅ Successfully loaded 500 records
🔍 Analyzing fleet performance...
✅ Fleet performance analysis complete
💡 Identifying optimization opportunities...
✅ Identified 3 optimization opportunities
💰 Total potential annual savings: $133,411.26
📊 Creating visualizations...
✅ Visualizations created
📄 Generating PDF report...
✅ PDF report generated: demo_fleet_audit.pdf
==================================================
🎉 Audit complete! Check your PDF report for detailed findings.

💰 POTENTIAL ANNUAL SAVINGS: $133,411.26
```

## 📁 Files Generated:
- `demo_fleet_audit.pdf` - Professional report to show clients
- `sample_trucking_data.csv` - Sample data for reference

## 🔧 Troubleshooting:

**"Python not found":**
- Make sure Python is installed and added to PATH
- Try `python3` instead of `python`

**"pip not found":**
- Try `pip3` instead of `pip`
- On Windows, try `py -m pip install -r requirements.txt`

**Permission errors:**
- On Mac/Linux, try `sudo pip3 install -r requirements.txt`
- On Windows, run Command Prompt as Administrator

## ⚡ Quick Test:
To verify everything works:
1. Run: `python --version` (should show Python 3.8+)
2. Run: `pip --version` (should show pip version)
3. Run: `python trucking_optimization_audit.py`
4. Check for PDF file creation