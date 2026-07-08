// Zero-dependency demo server for the seeded-bug feedback form.
// Usage: node demo/server.mjs   → http://localhost:8787
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const pagePath = join(dirname(fileURLToPath(import.meta.url)), 'index.html');

createServer((req, res) => {
  if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(readFileSync(pagePath));
  }
  if (req.method === 'POST' && req.url === '/api/feedback') {
    let body = '';
    req.on('data', (c) => (body += c));
    req.on('end', () => {
      console.log('POST /api/feedback', body);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end('{"ok":true}');
    });
    return;
  }
  res.writeHead(404).end();
}).listen(8787, () => console.log('Demo form: http://localhost:8787'));
