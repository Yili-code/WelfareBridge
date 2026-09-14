export const meta = {
  name: 'gold-labelling-round3',
  description: 'Label sampled documents from the new sources for the gold set: one agent per batch file reads every document and labels it; a second agent independently re-labels each batch so disagreements can be reviewed',
  phases: [
    { title: 'Label', detail: 'one agent per batch: read every document, output labels JSON' },
    { title: 'Cross-check', detail: 'independent second labelling of the same batch' },
  ],
}

const BRIEF = args.brief || 'data/round3/label_brief.md'
const OUT_DIR = args.outputDir || 'data/round3/labels'
const batches = args.batches

const LABEL_SCHEMA = {
  type: 'object',
  properties: {
    labels: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' }, title: { type: 'string' },
          is_benefit: { type: 'string', enum: ['yes', 'portal', 'no'] },
          kind: { type: 'string' },
          category: { type: 'string' }, secondary: { type: 'array', items: { type: 'string' } },
          closed: { type: 'boolean' }, reason: { type: 'string' },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['id', 'is_benefit', 'kind', 'category', 'secondary', 'reason', 'confidence'],
      },
    },
    count: { type: 'integer' },
  },
  required: ['labels', 'count'],
}

function labelPrompt(batch, pass) {
  return `你是黃金標註集的標註代理（第 ${pass} 次獨立標註）。先完整讀標註規則：${BRIEF}。

然後用 Read 完整讀這個批次檔：${batch}
檔裡每一份文件以「##### <id>」開頭。你必須逐份把 TEXT 讀完再判斷；不可以只看標題，不可以參考 SYSTEM 那一行。
批次檔有幾份文件，labels 就要有幾筆（count 填文件數）；id 一律照抄，不能編造。
category 與 secondary 只能用規則裡列出的 taxonomy id；不確定就 confidence 填 low 並在 reason 說明原文缺什麼。
另外把同樣的結果寫成 JSON 檔（{"labels": [...], "count": N}）存到 ${OUT_DIR}/${batch.split('/').pop().replace('.txt', '')}_pass${pass}.json（用 Write 工具，UTF-8）。`
}

phase('Label')
const results = await pipeline(
  batches,
  b => agent(labelPrompt(b, 1), { label: `label:${b.split('/').pop()}`, phase: 'Label', schema: LABEL_SCHEMA }),
  (r1, b) => agent(labelPrompt(b, 2), { label: `check:${b.split('/').pop()}`, phase: 'Cross-check', schema: LABEL_SCHEMA }).then(r2 => ({ batch: b, pass1: r1, pass2: r2 })),
)
const out = results.filter(Boolean)
let agree = 0, total = 0
for (const r of out) {
  const m2 = new Map((r.pass2 && r.pass2.labels || []).map(l => [l.id, l]))
  for (const l of (r.pass1 && r.pass1.labels || [])) {
    total++
    const o = m2.get(l.id)
    if (o && o.is_benefit === l.is_benefit && (o.category || '') === (l.category || '')) agree++
  }
}
log(`labelling done: ${out.length}/${batches.length} batches; gate+category agreement ${agree}/${total}`)
return out.map(r => ({ batch: r.batch, n1: (r.pass1 && r.pass1.labels || []).length, n2: (r.pass2 && r.pass2.labels || []).length }))
