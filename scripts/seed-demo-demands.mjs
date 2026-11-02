// 在訴求專區放 8 筆示範訴求（比賽 demo 用）。可重複執行：同一個 id 會被覆蓋，不會越放越多。
//   node scripts/seed-demo-demands.mjs            （WELFARE_DB_PATH 沒設就用 data/welfare.sqlite）
import { openDemands } from '../src/lib/server/demands.mjs';

export const DEMO_DEMANDS = [
  { id: 'demo-seed-01', title: '高雄市缺少失智長者的日間照顧名額', type: '失智照顧', region: '高雄市', detail: '申請日照要排半年以上，家屬白天要上班，只好請假在家看顧。', supports: 17, daysAgo: 21 },
  { id: 'demo-seed-02', title: '文山區夜間回診找不到長照接送', type: '交通接送', region: '臺北市文山區', detail: '復康巴士晚上六點後不受理，長輩夜間回診只能自費叫車。', supports: 14, daysAgo: 18 },
  { id: 'demo-seed-03', title: '外縣市大學生在臺北租屋，租金補貼要求設籍', type: '住宅與租金', region: '臺北市', detail: '學生戶籍在外縣市，不符合在地租金補貼資格，但實際租金負擔很重。', supports: 12, daysAgo: 15 },
  { id: 'demo-seed-04', title: '輪班家長需要夜間與假日托育', type: '育兒與托育', region: '新北市', detail: '公共托育只收白天，輪班的父母找不到可以放心托育的時段。', supports: 11, daysAgo: 12 },
  { id: 'demo-seed-05', title: '急難救助申請文件太多，第一次申請不知道從哪裡開始', type: '申請與給付', region: '臺中市', detail: '突然失去收入時需要快速協助，但要跑好幾個單位補件。', supports: 9, daysAgo: 8 },
  { id: 'demo-seed-06', title: '偏鄉高中生申請獎助學金沒有人協助填表', type: '就學與學費', region: '臺南市', detail: '學校人手不足，家長不熟悉線上申請，常常錯過期限。', supports: 6, daysAgo: 5 },
  { id: 'demo-seed-07', title: '偏遠地區缺少居家服務員', type: '居家照顧', region: '嘉義縣', detail: '核定了居家服務，卻等不到人員派案。', supports: 21, daysAgo: 40, status: 'claimed', owner: '嘉義縣政府社會局' },
  { id: 'demo-seed-08', title: '家庭照顧者想要有固定的喘息服務時段', type: '照顧者支持', region: '桃園市', detail: '喘息服務臨時申請常常額滿，希望可以預約固定時段。', supports: 25, daysAgo: 60, status: 'done', owner: '桃園市政府社會局', result: '已新增每月固定預約的喘息時段，可於社會局網站預約。' },
];

if (import.meta.url === `file://${process.argv[1].replace(/\\/g, '/')}` || process.argv[1]?.endsWith('seed-demo-demands.mjs')) {
  const db = openDemands();
  try {
    for (const item of DEMO_DEMANDS) db.seed(item);
    console.log(`已放入 ${DEMO_DEMANDS.length} 筆示範訴求`);
  } finally { db.close(); }
}
