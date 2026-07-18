import { createReadStream, existsSync, statSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, join, normalize, resolve, sep } from 'node:path';
import { createGzip } from 'node:zlib';

const MIME_TYPES = Object.freeze({
  '.avif': 'image/avif',
  '.css': 'text/css; charset=utf-8',
  '.gif': 'image/gif',
  '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon',
  '.jpeg': 'image/jpeg',
  '.jpg': 'image/jpeg',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.webp': 'image/webp',
  '.xml': 'application/xml; charset=utf-8'
});

function isCompressible(type) {
  return /^(?:text\/|application\/(?:javascript|json|manifest\+json|xml)|image\/svg\+xml)/.test(type);
}

export async function startStaticServer(rootDirectory, options = {}) {
  const root = resolve(rootDirectory);
  const server = createServer((request, response) => {
    const rawPath = decodeURIComponent((request.url || '/').split(/[?#]/, 1)[0]);
    const pathname = rawPath === '/' ? '/index.html' : rawPath;
    const candidate = normalize(join(root, pathname));

    if (candidate !== root && !candidate.startsWith(`${root}${sep}`)) {
      response.writeHead(403).end('Forbidden');
      return;
    }

    let filePath = candidate;
    if (existsSync(filePath) && statSync(filePath).isDirectory()) {
      filePath = join(filePath, 'index.html');
    }
    if (!existsSync(filePath) || !statSync(filePath).isFile()) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Not found');
      return;
    }

    const extension = extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[extension] || 'application/octet-stream';
    const headers = {
      'Content-Type': contentType,
      'Cache-Control': options.cacheControl || 'public, max-age=0, must-revalidate',
      'X-Content-Type-Options': 'nosniff'
    };
    const acceptsGzip = /\bgzip\b/.test(request.headers['accept-encoding'] || '');

    response.statusCode = 200;
    if (acceptsGzip && isCompressible(contentType)) {
      response.setHeader('Content-Encoding', 'gzip');
      response.setHeader('Vary', 'Accept-Encoding');
      Object.entries(headers).forEach(([name, value]) => response.setHeader(name, value));
      createReadStream(filePath).pipe(createGzip({ level: 6 })).pipe(response);
      return;
    }

    Object.entries(headers).forEach(([name, value]) => response.setHeader(name, value));
    response.setHeader('Content-Length', statSync(filePath).size);
    createReadStream(filePath).pipe(response);
  });

  await new Promise((resolveStart, reject) => {
    server.once('error', reject);
    server.listen(options.port || 0, '127.0.0.1', resolveStart);
  });
  const address = server.address();
  return {
    baseUrl: `http://127.0.0.1:${address.port}`,
    close: () => new Promise((resolveClose) => server.close(resolveClose))
  };
}
