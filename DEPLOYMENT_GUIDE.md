# NagarSeva Deployment Guide (Hackathon Ready 🚀)

This guide will help you host your project for free so you can present it live!

## 1. Backend Deployment (FastAPI)
I recommend using **Render.com** or **Railway.app** for the backend.

## 1. Backend Deployment (FastAPI Alternatives)

### Option A: Render.com (Solid Free Tier)
1.  **Create an account** on [Render.com](https://render.com).
2.  **New Web Service**: Click "New" -> "Web Service".
3.  **Connect GitHub**: Select your `nagarsewa_v2` repository.
4.  **Configure**:
    -   **Runtime**: `Python`
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `uvicorn api.index:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables**:
    -   Go to "Environment" and add:
        -   `GEMINI_API_KEY`: Your Gemini API Key.
        -   `ADMIN_USERNAME`: Your admin user.
        -   `ADMIN_PASSWORD`: Your admin password.
6.  **Deploy**: Once live, copy your URL.

### Option B: Railway.app (Easier Setup)
1.  **Sign up** at [Railway.app](https://railway.app).
2.  **New Project**: Click "+ New Project" -> "Deploy from GitHub repo".
3.  **Variables**: Add `GEMINI_API_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`.
4.  **Public URL**: Generate a domain in "Settings".

### Option C: Koyeb.com
1.  **Sign up** at [Koyeb.com](https://koyeb.com).
2.  **Configure**: Run Command should be `uvicorn api.index:app --host 0.0.0.0 --port 8000`.
3.  **Variables**: Add your keys in the dashboard.

---

## 2. Frontend Deployment (Netlify or Vercel)
Both platforms are excellent for hosting your UI.

### Option A: Netlify (Recommended)
1.  **Log in** to [Netlify](https://netlify.com).
2.  **Add new site**: Click "Add new site" -> "Import from GitHub".
3.  **Configure**:
    -   **Base directory**: `nagarseva`
    -   **Publish directory**: `.` (relative to base)
4.  **Deploy**: Click "Deploy site".

### Option B: Vercel
1.  **Login** to [Vercel](https://vercel.com) with GitHub.
2.  **Add New Project**: Select your `nagarsewa_v2` repository.
3.  **Root Directory**: Set this to `nagarseva`.
4.  **Deploy**: Click "Deploy".

---

## 3. Unified Deployment (Vercel)
If you want **everything (Frontend + Backend) on a single URL**, I have already created a `vercel.json` in your root folder.

### Steps for Unified Vercel:
1.  **Login** to [Vercel](https://vercel.com).
2.  **Add New Project**: Select your `nagarsewa_v2` repository.
3.  **No Configuration Needed**: Vercel will automatically detect the `vercel.json` and host your FastAPI app at `/api` and your UI at `/`.
4.  **Environment Variables**: Just add your `GEMINI_API_KEY` in the Vercel Settings.

---

## 3. GitHub Strategy
1.  **Initialize Git**: `git init` in your main project folder.
2.  **Add all files**: `git add .`
3.  **Commit**: `git commit -m "Hackathon Ready Release"`
4.  **Remote**: Link to your GitHub Repo and `git push origin main`.

---

## 💡 Hackathon Pro-Tip
Since the free tier of Render "goes to sleep" after 15 minutes of inactivity, open your backend URL in a tab 2 minutes before your final presentation to wake it up! ⚡️
