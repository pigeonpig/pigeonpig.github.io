import fs from 'fs/promises';
import path from 'path';

const API_BASE = process.env.API_BASE;
const OUTPUT = 'docs';

if (!API_BASE) {
  console.error('API_BASE env not set');
  process.exit(1);
}

async function fetchJson(url, out) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed ${url}: ${res.status}`);
  const data = await res.json();
  await fs.mkdir(path.dirname(out), { recursive: true });
  await fs.writeFile(out, JSON.stringify(data, null, 2));
  return data;
}

async function fetchText(url, out) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed ${url}: ${res.status}`);
  const text = await res.text();
  await fs.mkdir(path.dirname(out), { recursive: true });
  await fs.writeFile(out, text);
  return text;
}

(async () => {
  await fs.rm(OUTPUT, { recursive: true, force: true });
  await fs.mkdir(OUTPUT, { recursive: true });

  const staticFiles = ['main.html', 'ideas.html', 'admin.html', 'sw.js'];
  for (const f of staticFiles) {
    await fs.copyFile(f, path.join(OUTPUT, f));
  }

  const wxData = await fetchJson(`${API_BASE}/api/wx`, path.join(OUTPUT, 'api/wx'));
  await fetchJson(`${API_BASE}/api/daily`, path.join(OUTPUT, 'api/daily'));

  for (const meta of Object.values(wxData)) {
    if (meta && meta.abbrlink) {
      await fetchText(`${API_BASE}/api/article?abbr=${meta.abbrlink}`, path.join(OUTPUT, 'articles', `${meta.abbrlink}.html`));
    }
  }
})();
