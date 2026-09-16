import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { openDemands, THRESHOLD } from '../src/lib/server/demands.mjs';

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
