import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';

export function openAppeals(path = process.env.WELFARE_DB_PATH || resolve('data/welfare.sqlite')) {
  mkdirSync(dirname(path), { recursive: true });
  const db = new DatabaseSync(path);
  db.exec("PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000; CREATE TABLE IF NOT EXISTS appeals (id TEXT PRIMARY KEY, body TEXT NOT NULL, created_at TEXT NOT NULL)");
  return {
    list() { return db.prepare('SELECT body FROM appeals ORDER BY created_at DESC, rowid DESC').all().map(row => JSON.parse(row.body)); },
    create(input, key) {
      const appeal = { ...input, id: key || randomUUID(), status: 'new', createdAt: new Date().toISOString() };
      db.prepare('INSERT OR IGNORE INTO appeals VALUES (?, ?, ?)').run(appeal.id, JSON.stringify(appeal), appeal.createdAt);
      return { id: appeal.id };
    },
    update(id, status) {
      return db.prepare("UPDATE appeals SET body = json_set(body, '$.status', ?) WHERE id = ?").run(status, id).changes > 0;
    },
    close() { db.close(); },
  };
}
