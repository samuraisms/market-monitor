# Market Monitor: setup (about 5 minutes)

1. Create a free account at github.com, then a new **public** repository (e.g. `market-monitor`).
2. Upload everything in this folder, including the hidden `.github` folder (drag and drop works; or use "Add file > Upload files").
3. Repo **Settings > Pages**: Source = "Deploy from a branch", Branch = `main`, folder `/ (root)`. Save.
4. Repo **Settings > Actions > General > Workflow permissions**: choose "Read and write permissions". Save.
5. Open the **Actions** tab > "Update Market Monitor" > **Run workflow**. The first run takes 10 to 30 minutes.
6. Your dashboard is at `https://YOUR-USERNAME.github.io/market-monitor/`. Bookmark it on your phone.

It then updates itself every weekday after the close. History builds up one row per day.
Tune `MIN_PRICE` and `MIN_VOLUME` at the top of `scan.py` to match your own scan filters.
