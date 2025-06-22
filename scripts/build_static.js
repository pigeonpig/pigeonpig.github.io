import fs from 'fs/promises';
import path from 'path';

const API_BASE = process.env.API_BASE;
if (!API_BASE) {
  console.error('API_BASE environment variable is required');
  process.exit(1);
}

const dist = path.resolve('dist');
const apiDir = path.join(dist, 'api');
const articleDir = path.join(dist, 'articles');

await fs.rm(dist, { recursive: true, force: true });
await fs.mkdir(apiDir, { recursive: true });
await fs.mkdir(articleDir, { recursive: true });

async function fetchJSON(url) {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`${url} ${res.status}`);
  return res.json();
}

async function fetchText(url) {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`${url} ${res.status}`);
  return res.text();
}

// copy and patch html/js files
for (const file of ['main.html', 'ideas.html', 'admin.html', 'sw.js']) {
  let content = await fs.readFile(file, 'utf8');
  content = content.replace(/\/api\/wx/g, 'api/wx.json');
  content = content.replace(/\/api\/daily/g, 'api/daily.json');
  content = content.replace(/`\/api\/article\?url=\$\{encodeURIComponent\(url\)\}`/g,
    '`articles/${encodeURIComponent(url)}.html`');
  content = content.replace(/fetchWithFallback\(`\/api\/article\?url=\$\{encodeURIComponent\(url\)\}`/g,
    'fetchWithFallback(`articles/${encodeURIComponent(url)}.html`');
  await fs.writeFile(path.join(dist, file), content);
}

const wxData = await fetchJSON('/api/wx');
await fs.writeFile(path.join(apiDir, 'wx.json'), JSON.stringify(wxData, null, 2));
const dailyData = await fetchJSON('/api/daily');
await fs.writeFile(path.join(apiDir, 'daily.json'), JSON.stringify(dailyData, null, 2));

for (const item of Object.values(wxData)) {
  if (!item || !item.url) continue;
  const html = await fetchText(`/api/article?url=${encodeURIComponent(item.url)}`);
  const fileName = encodeURIComponent(item.url) + '.html';
  await fs.writeFile(path.join(articleDir, fileName), html);
}
