Reality Check Detector - Professional ZIP
========================================

This package provides a deployable PWA frontend and a FastAPI backend with:
- User registration & login (token-based)
- Submission tracking in SQLite (journalist workflow)
- Explainable heuristics + optional external or Hugging Face detector integration
- Press verification dashboard (view & mark verified)

Quick deploy (phone):
1. Create a new GitHub repo and upload this ZIP via 'Add file -> Upload files'.
2. Deploy backend on Render.com (New > Web Service). Use Root: /api and Start Command: uvicorn main:app --host 0.0.0.0 --port 8080. Add env vars if needed:
   - DETECTOR_TYPE=hf or external or mock
   - DETECTOR_API=https://your-detector.example/analyze
   - HUGGINGFACE_API_KEY=...
   - HF_MODEL=your-hf-model
3. Deploy frontend (web/) to Vercel or GitHub Pages. If backend is on different domain, edit web/js/app.js fetch URL (replace '/api/analyze' with full backend URL).
4. Sign in (Register), upload files, and view submissions in Dashboard.
