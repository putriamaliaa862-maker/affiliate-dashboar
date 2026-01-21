# 🔧 FIX GIT PUSH ERROR

## ❌ Error yang muncul:
```
error: src refspec main does not match any
error: failed to push some refs to 'https://github.com/putriamaliaa862-maker/affiliate-dashboar.git'
```

## ✅ Solusi: Lakukan step-step berikut

### Step 1: Cek status Git
```bash
git status
```

### Step 2: Add semua files
```bash
git add .
```

### Step 3: Commit files
```bash
git commit -m "Initial commit - Supabase migration ready"
```

### Step 4: Cek branch name
```bash
git branch
```

Jika outputnya `* master` (bukan main), gunakan:
```bash
git push -u origin master
```

Atau rename branch ke main:
```bash
git branch -M main
git push -u origin main
```

### Step 5: Push ke GitHub
```bash
git push -u origin main
```

---

## 🚀 COMMAND LENGKAP (Copy-paste semua):

```bash
# 1. Cek status
git status

# 2. Add semua files
git add .

# 3. Commit
git commit -m "Initial commit - Supabase migration ready"

# 4. Rename branch ke main (jika perlu)
git branch -M main

# 5. Push
git push -u origin main
```

---

## ⚠️ Jika masih error, coba:

### Option A: Force rename branch
```bash
git branch -M main
git push -u origin main
```

### Option B: Cek remote URL
```bash
git remote -v
```

Jika URL salah, fix dengan:
```bash
git remote set-url origin https://github.com/putriamaliaa862-maker/affiliate-dashboar.git
```

### Option C: Set default branch
```bash
git config --global init.defaultBranch main
git branch -M main
git push -u origin main
```

---

## 📝 NOTES

- **Jangan lupa commit dulu!** Error muncul karena belum ada commit
- Repository name: `affiliate-dashboar` (perhatikan typo di GitHub)
- Username: `putriamaliaa862-maker`

---

**Coba step-step di atas, harusnya berhasil!** ✅