# School Management System — Railway Deployment

A single-file HTML school management app backed by Flask + SQLite, deployable to Railway in minutes.

---

## Project Structure

```
school-app/
├── server.py          ← Flask backend (API + static file serving)
├── requirements.txt   ← Python dependencies
├── Procfile           ← How Railway/gunicorn starts the app
├── railway.toml       ← Railway build & deploy config
├── .gitignore
├── data/              ← Created automatically; holds school.db (NOT committed)
└── public/
    └── index.html     ← Your school management frontend
```

---

## Deploy to Railway — Step by Step

### 1. Push to GitHub

```bash
# In this folder:
git init
git add .
git commit -m "Initial commit — school management system"

# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/school-app.git
git push -u origin main
```

### 2. Create a Railway project

1. Go to **railway.app** → **New Project**
2. Choose **Deploy from GitHub repo**
3. Select your `school-app` repository
4. Railway auto-detects Python and builds with Nixpacks — no extra config needed

### 3. Add a Persistent Volume (important!)

Railway containers reset on every deploy — the `data/` folder is wiped unless you attach a volume.

1. In your Railway project, click **+ New** → **Volume**
2. Set **Mount Path** to `/app/data`
3. Railway will now persist `school.db` across deploys and restarts

### 4. Set environment variables (optional)

| Variable  | Default          | Purpose                          |
|-----------|------------------|----------------------------------|
| `DB_PATH` | `data/school.db` | Override the SQLite file location |

Railway sets `PORT` automatically — you don't need to add it.

### 5. Open your app

Railway gives you a public URL like `https://school-app-production.up.railway.app`.
Open it and log in as usual.

---

## Local Development

```bash
pip install -r requirements.txt
python server.py
# Open http://localhost:5000
```

---

## Data & Backups

- All data is saved automatically to `data/school.db` on the Railway volume.
- Use the **Export** button inside the app to download a `.json` backup to your laptop at any time.
- Use **Import** to restore from a backup (replaces all current data).

---

## Notes

- The app supports **multiple simultaneous users** — if two people save at the same time, the second user gets a conflict warning and the latest data is loaded automatically.
- Live sync polls every 5 seconds, so changes from one device appear on others quickly.
- SQLite is fine for a school with up to a few hundred users. If you need more scale later, the backend can be swapped to PostgreSQL without changing `index.html`.
