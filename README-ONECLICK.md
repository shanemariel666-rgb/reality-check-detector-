# Reality Check — One-Click Deploy (Render + Vercel)

This repository is prepared for one-click deploy. Follow these steps **on your phone**:

1. **Create a GitHub repo** and upload all files from this project (you can upload the ZIP to GitHub via mobile).

2. **Deploy backend to Render (one-click):**
   - Tap: https://dashboard.render.com/new/web/service?repo=https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
   - On Render, confirm settings. The `render.yaml` file is included to preconfigure the service. Set environment variables if you use external detectors:
     - `DETECTOR_TYPE` = `hf` or `external` or `mock`
     - `DETECTOR_API` = (optional)
     - `HUGGINGFACE_API_KEY` = (optional)
     - `HF_MODEL` = (optional)

3. **Deploy frontend to Vercel (one-click):**
   - Tap: https://vercel.com/new/git/external?repository-url=https://github.com/YOUR_USERNAME/YOUR_REPO_NAME&project-name=reality-check-frontend
   - In Vercel import settings, set the Root Directory to `/web` and deploy.

4. **Configure GitHub Secrets (for automatic deployments)** (optional):
   - `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`, `RENDER_API_KEY`

5. **Open the frontend URL** provided by Vercel, register as a journalist, and start uploading files.

---

If you want me to generate the GitHub repo for you (I can't push to your account, but I can give exact copy-paste steps), tell me your GitHub username and I'll tailor the README and render links automatically.
