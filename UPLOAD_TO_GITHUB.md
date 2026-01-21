# 📤 UPLOAD KE GITHUB - Panduan Lengkap

> **Step-by-step untuk upload code ke GitHub repository**

---

## 📋 PREREQUISITES

Sebelum mulai, pastikan sudah punya:
- ✅ GitHub account (sign up di https://github.com)
- ✅ Git installed di komputer (download: https://git-scm.com)
- ✅ Code project sudah di folder lokal

---

## 🚀 OPTION 1: Upload via GitHub Desktop (MUDAH!)

### Step 1: Install GitHub Desktop

1. Download: https://desktop.github.com
2. Install & login dengan GitHub account

### Step 2: Create Repository di GitHub

1. Buka https://github.com
2. Click **"+"** → **"New repository"**
3. Isi:
   - **Name:** `affiliate-dashboard`
   - **Description:** (optional)
   - **Visibility:** Public atau Private
4. **JANGAN** centang "Initialize with README"
5. Click **"Create repository"**

### Step 3: Clone Repository

1. Di GitHub Desktop, click **"File"** → **"Clone repository"**
2. Atau di GitHub website, click **"Code"** → **"Open with GitHub Desktop"**
3. Pilih folder untuk clone (misalnya: `C:\Users\PC\Downloads\`)
4. Click **"Clone"**

### Step 4: Copy Files ke Repository

1. Copy semua files dari `affiliate-dashboard` ke folder yang baru di-clone
2. Paste semua files ke dalam folder repository

### Step 5: Commit & Push

1. GitHub Desktop akan detect changes
2. Di left panel, semua files akan muncul
3. Di bottom, isi:
   - **Summary:** `Initial commit - Supabase migration ready`
   - **Description:** (optional)
4. Click **"Commit to main"**
5. Click **"Push origin"** (atau **"Publish repository"** jika pertama kali)

### Step 6: Verify

1. Buka https://github.com/your-username/affiliate-dashboard
2. Semua files harusnya sudah ada di GitHub ✅

---

## 💻 OPTION 2: Upload via Git Command Line (Tradisional)

### Step 1: Install Git

1. Download: https://git-scm.com/download/win
2. Install dengan default settings
3. Verify: buka Command Prompt, ketik `git --version`

### Step 2: Create Repository di GitHub

1. Buka https://github.com
2. Click **"+"** → **"New repository"**
3. Isi:
   - **Name:** `affiliate-dashboard`
   - **Visibility:** Public atau Private
4. **JANGAN** centang "Initialize with README"
5. Click **"Create repository"**

### Step 3: Initialize Git di Project Folder

1. Buka Command Prompt / PowerShell
2. Navigate ke folder project:
   ```bash
   cd C:\Users\PC\Downloads\affiliate-dashboard
   ```
3. Initialize Git:
   ```bash
   git init
   ```

### Step 4: Configure Git (Jika Pertama Kali)

1. Set username:
   ```bash
   git config --global user.name "Your Name"
   ```
2. Set email:
   ```bash
   git config --global user.email "your.email@example.com"
   ```

### Step 5: Add Files & Commit

1. Add semua files:
   ```bash
   git add .
   ```
2. Commit:
   ```bash
   git commit -m "Initial commit - Supabase migration ready"
   ```

### Step 6: Connect ke GitHub & Push

1. Add remote repository (ganti `your-username` dengan username GitHub):
   ```bash
   git remote add origin https://github.com/your-username/affiliate-dashboard.git
   ```
2. Rename branch ke main (jika perlu):
   ```bash
   git branch -M main
   ```
3. Push ke GitHub:
   ```bash
   git push -u origin main
   ```
4. Akan diminta login GitHub (username & password/token)

### Step 7: Verify

1. Buka https://github.com/your-username/affiliate-dashboard
2. Semua files harusnya sudah ada ✅

---

## 🔐 AUTHENTICATION: Personal Access Token

Jika push gagal dengan password, perlu pakai **Personal Access Token**:

### Step 1: Generate Token

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token"**
3. Isi:
   - **Note:** `Git Push Token`
   - **Expiration:** 90 days (atau pilih sendiri)
   - **Scopes:** Centang **`repo`** (full control)
4. Click **"Generate token"**
5. **COPY TOKEN INI!** (hanya muncul sekali)

### Step 2: Use Token

Saat push, ketika diminta password:
- **Username:** GitHub username Anda
- **Password:** Paste token yang sudah dicopy (bukan password GitHub!)

---

## 📝 CREATE .gitignore (PENTING!)

Sebelum push, pastikan ada file `.gitignore` untuk exclude file yang tidak perlu:

### File `.gitignore` (di root folder):

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.db
*.sqlite
*.sqlite3

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Environment variables
.env
.env.local
.env.production
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build outputs
dist/
build/
*.egg-info/

# Logs
*.log
logs/

# Database
*.db
*.sqlite
affiliate.db
test.db

# Extension
extension/dist/
extension/*.zip
*.crx
*.pem

# Archives
*.rar
*.zip
*.tar.gz
*.rar
extension.rar
```

### Add .gitignore

1. Buat file `.gitignore` di root folder
2. Copy paste isi di atas
3. Save
4. Commit:
   ```bash
   git add .gitignore
   git commit -m "Add .gitignore"
   git push
   ```

---

## ✅ CHECKLIST SEBELUM PUSH

Sebelum push, pastikan:

- [ ] ✅ `.gitignore` sudah ada (exclude `.env`, `venv`, `node_modules`)
- [ ] ✅ `.env` file **TIDAK** di-commit (sensitive data!)
- [ ] ✅ Tidak ada password atau API keys di code
- [ ] ✅ Semua dependencies ada di `requirements.txt` dan `package.json`

---

## 🔄 UPDATE CODE SETELAH PUSH

Setelah push pertama, untuk update code di GitHub:

### Via GitHub Desktop:
1. Edit files
2. GitHub Desktop akan detect changes
3. Commit dengan message
4. Click **"Push origin"**

### Via Command Line:
```bash
# Add changes
git add .

# Commit
git commit -m "Update: description of changes"

# Push
git push
```

---

## 🎯 NEXT STEPS

Setelah code di GitHub:

1. ✅ **Deploy Backend ke Railway**
   - Railway akan connect ke GitHub repo
   - Auto-deploy dari GitHub

2. ✅ **Deploy Frontend ke Vercel**
   - Vercel akan connect ke GitHub repo
   - Auto-deploy dari GitHub

---

## 📚 RESOURCES

- [Git Download](https://git-scm.com/download/win)
- [GitHub Desktop](https://desktop.github.com)
- [GitHub Docs](https://docs.github.com)
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)

---

## ⚠️ TROUBLESHOOTING

### Error: "Repository not found"

**Solution:**
- Cek repository name benar
- Cek username benar
- Pastikan repository sudah dibuat di GitHub

### Error: "Authentication failed"

**Solution:**
- Pakai Personal Access Token (bukan password)
- Generate token baru di GitHub Settings

### Error: "Large file" atau push terlalu lama

**Solution:**
- Pastikan `.gitignore` sudah benar
- Jangan push `node_modules`, `venv`, atau database files
- Jika file terlalu besar, consider Git LFS

---

**Status:** Ready untuk Upload! 🚀

**Recommendation:** Pakai **GitHub Desktop** (lebih mudah untuk pemula!)