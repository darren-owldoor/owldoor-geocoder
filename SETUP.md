# GitHub Setup Instructions

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `owldoor-geocoder`
3. Description: "Simple geocoding tool using OpenStreetMap"
4. Make it **Public** (required for free GitHub Pages)
5. **DO NOT** initialize with README, .gitignore, or license (we already have files)
6. Click "Create repository"

## Step 2: Push Your Code

After creating the repository, run:

```bash
cd /Users/Darren/Downloads/owldoor-geocoder
git push -u origin main
```

If you get authentication errors, you may need to:
- Use a Personal Access Token instead of password
- Or set up SSH keys

## Step 3: Enable GitHub Pages

1. Go to: https://github.com/ydarren-owldoor/owldoor-geocoder/settings/pages
2. Under "Source", select **"main"** branch
3. Click **Save**
4. Your geocoder will be live at: https://ydarren-owldoor.github.io/owldoor-geocoder

## Alternative: Create Repository via GitHub CLI

If you have GitHub CLI installed:

```bash
gh repo create owldoor-geocoder --public --source=. --remote=origin --push
```

