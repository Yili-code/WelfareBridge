import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { openDemands, THRESHOLD } from '../src/lib/server/demands.mjs';
import { DEMO_DEMANDS } from '../scripts/seed-demo-demands.mjs';

test('a confirmed assistant request is published once as a Demo demand, and seeded demos show the right statuses', () => {
  const folder = mkdtempSync(join(tmpdir(), 'welfare-demands-'));
  let db;
  try {
    db = openDemands(join(folder, 'test.sqlite'));
    const item = { id: 'idempotency-key-0001', title: '高雄失智症照護資源', type: '失智照顧', region: '高雄市', detail: '摘要' };
    assert.equal(db.createFromAppeal(item, item.id).demo, true);
    db.createFromAppeal(item, item.id);
    assert.equal(db.list().filter(d => d.demo).length, 1, 'same key must not publish twice');
    assert.equal(db.list().find(d => d.demo).supports, 1);

    for (const demo of DEMO_DEMANDS) db.seed(demo);
    for (const demo of DEMO_DEMANDS) db.seed(demo);
    const all = db.list();
    assert.equal(all.length, DEMO_DEMANDS.length + 1, 'seeding twice must not duplicate');
    assert.equal(all.filter(d => d.status === 'pending').length, 4);
    assert.equal(all.filter(d => d.status === 'collecting').length, 3, 'two seeded plus the new Demo request');
    assert.equal(all.find(d => d.id === 'demo-seed-07').status, 'claimed');
    assert.equal(all.find(d => d.id === 'demo-seed-08').status, 'done');
    assert.equal(all.find(d => d.id === 'demo-seed-01').demo, false);
  } finally { db?.close(); rmSync(folder, { recursive: true }); }
});

test('each browser supports a demand once; reaching the threshold makes it pending; staff can claim it', () => {
  const folder = mkdtempSync(join(tmpdir(), 'welfare-demands-'));
  let db;
  try {
    db = openDemands(join(folder, 'test.sqlite'));
    const created = db.create({ title: '文山區缺少夜間長照接送', type: '交通接送', region: '臺北市文山區', detail: '晚上回診找不到車' }, 'voter-author-000001');
    assert.equal(created.supports, 1);
    assert.equal(created.status, 'collecting');
    assert.equal(created.voted, true);
    assert.equal(db.list('someone-else-0000001')[0].voted, false);

    assert.equal(db.support(created.id, 'voter-author-000001').supports, 1, 'the author already counts as one support');
    let item;
    for (let i = 2; i <= THRESHOLD; i += 1) item = db.support(created.id, `voter-${String(i).padStart(14, '0')}`);
    assert.equal(item.supports, THRESHOLD);
    assert.equal(item.status, 'pending');
    assert.equal(db.support('missing', 'voter-00000000000001'), null);

    assert.equal(db.update(created.id, { status: 'claimed', owner: '臺北市政府衛生局' }), true);
    assert.equal(db.get(created.id).status, 'claimed');
    assert.equal(db.get(created.id).owner, '臺北市政府衛生局');
  } finally { db?.close(); rmSync(folder, { recursive: true }); }
});
