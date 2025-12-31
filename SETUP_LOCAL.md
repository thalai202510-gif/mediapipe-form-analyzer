# Local Setup Guide with ngrok (FREE)

## 🎯 Overview
This guide will help you run the MediaPipe Form Analyzer locally and expose it via ngrok so n8n can access it.

## 📋 Prerequisites
- Python 3.11+ installed
- Git installed
- Internet connection

## 🚀 Step-by-Step Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/thalai202510-gif/mediapipe-form-analyzer.git
cd mediapipe-form-analyzer
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Flask App
```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Step 5: Install and Setup ngrok (FREE)

1. **Download ngrok:**
   - Go to: https://ngrok.com/download
   - Sign up for free account
   - Download ngrok for your OS

2. **Install ngrok:**
   - Windows: Extract and move ngrok.exe to a folder in PATH
   - Mac: `brew install ngrok` or extract to /usr/local/bin
   - Linux: `sudo snap install ngrok`

3. **Authenticate ngrok:**
   ```bash
   ngrok authtoken YOUR_AUTH_TOKEN
   ```
   (Get your auth token from ngrok dashboard)

4. **Start ngrok tunnel:**
   ```bash
   ngrok http 5000
   ```

5. **Copy your public URL:**
   You'll see something like:
   ```
   Forwarding  https://1234-abc-xyz.ngrok.io -> http://localhost:5000
   ```

### Step 6: Test the API

Test the health endpoint:
```bash
curl https://YOUR-NGROK-URL.ngrok.io/health
```

You should get:
```json
{"status":"healthy","service":"mediapipe-form-analysis"}
```

## 🔌 Connect to n8n

### In your n8n workflow:

1. **Add HTTP Request node**
2. **Configure:**
   - Method: POST
   - URL: `https://YOUR-NGROK-URL.ngrok.io/analyze`
   - Body (JSON):
   ```json
   {
     "videoUrl": "YOUR_VIDEO_URL",
     "exerciseType": "squat"
   }
   ```

3. **Response format:**
   ```json
   {
     "success": true,
     "formScore": 8.5,
     "maxScore": 10,
     "metrics": [
       {
         "metric": "depth",
         "score": 9.0,
         "feedback": "Perfect depth - hitting parallel or below"
       }
     ],
     "recommendations": [
       "Great form overall! Keep it up."
     ],
     "framesAnalyzed": 90
   }
   ```

## ⚙️ Configuration

### Supported Exercise Types:
- `squat` (default)
- `deadlift`

### API Endpoints:
- `GET /health` - Health check
- `POST /analyze` - Analyze exercise form

## 🎬 Example n8n Workflow

```
[Webhook Trigger] 
    ↓
[HTTP Request to /analyze]
    ↓
[Process Response]
    ↓
[Send Results]
```

## 💡 Tips

1. **Keep Flask running:** Don't close the terminal running `python app.py`
2. **Keep ngrok running:** Don't close the terminal running `ngrok http 5000`
3. **ngrok URL changes:** Free ngrok URLs change when you restart. Update n8n workflow accordingly.
4. **Static URL (Optional):** Upgrade to ngrok paid plan ($8/mo) for static URL

## 🐛 Troubleshooting

### Flask won't start:
```bash
# Check if port 5000 is in use
# Windows: netstat -ano | findstr :5000
# Mac/Linux: lsof -i :5000

# Use different port
python app.py  # Edit app.py to change port
```

### MediaPipe errors:
```bash
# Reinstall dependencies
pip uninstall opencv-python-headless mediapipe
pip install opencv-python-headless==4.8.1.78 mediapipe==0.10.9
```

### ngrok not working:
- Check firewall settings
- Verify ngrok authtoken is correct
- Try different port: `ngrok http 5001`

## 📊 Performance

- Processing time: ~5-10 seconds per video (90 frames)
- Memory usage: ~500MB-1GB
- Requires: 2GB RAM minimum

## 🔒 Security

- ngrok URLs are random and hard to guess
- Free tier has 40 requests/minute limit
- Don't share your ngrok URL publicly

## ✅ Advantages of Local + ngrok

✅ **100% FREE** (ngrok free tier)
✅ **Full MediaPipe power** (your local CPU/GPU)
✅ **Easy debugging** (see logs in real-time)
✅ **No deployment issues**
✅ **Works immediately**

## 📝 Next Steps

1. Clone the repo
2. Follow steps 1-6
3. Test with n8n
4. Build your fitness app! 💪

---

**Need help?** Open an issue on GitHub!
