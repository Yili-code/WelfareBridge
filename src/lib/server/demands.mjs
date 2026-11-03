import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';

/** 同類型訴求累積達這個附議數即進入「待認領」 */
export const THRESHOLD = 10;

/**
 * 訴求專區（公開）：使用者提出的服務缺口與附議。
 * 和聊天助理的「需求登記」（appeals.mjs，只有承辦人員看得到）分開存放——這裡的內容會公開給所有人看。
 * 顯示狀態：collecting 蒐集中 → pending 待認領（附議達門檻）→ claimed 已認領 → done 已實現。
 */
export function openDemands(path = process.env.WELFARE_DB_PATH || resolve('data/welfare.sqlite')) {
  mkdirSync(dirname(path), { recursive: true });
  const db = new DatabaseSync(path);
  db.exec(`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;
    CREATE TABLE IF NOT EXISTS demands (id TEXT PRIMARY KEY, title TEXT NOT NULL, type TEXT NOT NULL, region TEXT NOT NULL, detail TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'open', owner TEXT NOT NULL DEFAULT '', result TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS demand_supports (demand_id TEXT NOT NULL, voter TEXT NOT NULL, created_at TEXT NOT NULL, PRIMARY KEY (demand_id, voter));`);
  // demo=1：小幫手摘要送出後自動公開到這裡的需求（畫面上標示 Demo）
  if (!db.prepare("SELECT 1 FROM pragma_table_info('demands') WHERE name = 'demo'").get()) db.exec('ALTER TABLE demands ADD COLUMN demo INTEGER NOT NULL DEFAULT 0');
  const shape = (row, voter) => {
    if (!row) return null;
    const supports = Number(row.supports);
    const status = row.status === 'open' ? (supports >= THRESHOLD ? 'pending' : 'collecting') : row.status;
    return { id: row.id, title: row.title, type: row.type, region: row.region, detail: row.detail, status, owner: row.owner, result: row.result, supports, created: row.created_at.slice(0, 10), voted: Boolean(voter) && Boolean(row.voted), demo: Boolean(row.demo) };
  };
  const select = `SELECT d.*, (SELECT COUNT(*) FROM demand_supports s WHERE s.demand_id = d.id) AS supports,
    EXISTS(SELECT 1 FROM demand_supports s WHERE s.demand_id = d.id AND s.voter = ?) AS voted FROM demands d`;
  return {
    list(voter = '') {
      return db.prepare(`${select} ORDER BY supports DESC, d.created_at DESC`).all(voter).map(row => shape(row, voter));
    },
    get(id, voter = '') {
      return shape(db.prepare(`${select} WHERE d.id = ?`).get(voter, id), voter);
    },
    create({ title, type, region, detail }, voter) {
      const id = randomUUID();
      const now = new Date().toISOString();
      db.exec('BEGIN');
      try {
        db.prepare('INSERT INTO demands (id, title, type, region, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)').run(id, title, type, region, detail, now);
        db.prepare('INSERT OR IGNORE INTO demand_supports VALUES (?, ?, ?)').run(id, voter, now);  // 提出的人算第一則附議
        db.exec('COMMIT');
      } catch (error) { db.exec('ROLLBACK'); throw error; }
      return this.get(id, voter);
    },
    /** 小幫手的需求登記送出後同步公開：以送出識別碼當 id，同一份登記重送不會重複出現。 */
    createFromAppeal({ id, title, type, region, detail }, voter) {
      const now = new Date().toISOString();
      db.exec('BEGIN');
      try {
        db.prepare('INSERT OR IGNORE INTO demands (id, title, type, region, detail, demo, created_at) VALUES (?, ?, ?, ?, ?, 1, ?)').run(id, title, type, region, detail, now);
        db.prepare('INSERT OR IGNORE INTO demand_supports VALUES (?, ?, ?)').run(id, voter, now);
        db.exec('COMMIT');
      } catch (error) { db.exec('ROLLBACK'); throw error; }
      return this.get(id, voter);
    },
    /** 預先放的示範訴求：附議數用不重複的假瀏覽器識別碼補足，之後仍可照常附議。 */
    seed({ id, title, type, region, detail, supports, status = 'open', owner = '', result = '', daysAgo = 0 }) {
      const created = new Date(Date.now() - daysAgo * 86_400_000).toISOString();
      db.exec('BEGIN');
      try {
        db.prepare('INSERT OR REPLACE INTO demands (id, title, type, region, detail, status, owner, result, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)').run(id, title, type, region, detail, status, owner, result, created);
        db.prepare('DELETE FROM demand_supports WHERE demand_id = ?').run(id);
        for (let i = 1; i <= supports; i += 1) db.prepare('INSERT INTO demand_supports VALUES (?, ?, ?)').run(id, `seed-${id}-${String(i).padStart(3, '0')}`, created);
        db.exec('COMMIT');
      } catch (error) { db.exec('ROLLBACK'); throw error; }
    },
    /** 同一個瀏覽器對同一則訴求只算一次 */
    support(id, voter) {
      if (!db.prepare('SELECT 1 FROM demands WHERE id = ?').get(id)) return null;
      db.prepare('INSERT OR IGNORE INTO demand_supports VALUES (?, ?, ?)').run(id, voter, new Date().toISOString());
      return this.get(id, voter);
    },
    update(id, { status, owner = '', result = '' }) {
      return db.prepare('UPDATE demands SET status = ?, owner = ?, result = ? WHERE id = ?').run(status, owner, result, id).changes > 0;
    },
    /** 刪除一則訴求與它的附議；小幫手送出的訴求和需求登記共用 id，由呼叫端一併刪登記 */
    remove(id) {
      db.exec('BEGIN');
      try {
        db.prepare('DELETE FROM demand_supports WHERE demand_id = ?').run(id);
        const removed = db.prepare('DELETE FROM demands WHERE id = ?').run(id).changes > 0;
        db.exec('COMMIT');
        return removed;
      } catch (error) { db.exec('ROLLBACK'); throw error; }
    },
    close() { db.close(); },
  };
}
