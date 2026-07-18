#!/usr/bin/env node

import { resolve } from 'node:path';
import process from 'node:process';
import { startStaticServer } from './lib/static-server.mjs';

const root = resolve(process.argv[2] || 'dist');
const port = Number(process.env.PORT || 4173);
const server = await startStaticServer(root, {
  port,
  cacheControl: process.env.PERF_CACHE_CONTROL || 'public, max-age=0, must-revalidate'
});

process.stdout.write(`Serving ${root} at ${server.baseUrl}\n`);
for (const signal of ['SIGINT', 'SIGTERM']) {
  process.once(signal, async () => {
    await server.close();
    process.exit(0);
  });
}
