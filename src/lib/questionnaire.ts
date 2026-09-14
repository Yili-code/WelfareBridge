import type { Profile } from './types';
export interface Question { key: string; title: string; why: string; multi?: boolean; options: string[] }
export const QUESTIONS: Question[] = [
 { key: 'needs', title: '你目前最需要哪方面的補助？', why: '先確認需求，安排推薦順序；其他可能適用的補助仍會保留。', multi: true, options: ['就學、學費或獎助學金', '求職、失業或職業訓練', '租屋、住宅或居住改善', '生活費、育兒或急難救助', '醫療、身心障礙或長期照顧'] },
 { key: 'age', title: '申請補助的對象目前幾歲？', why: '青年、兒少與老人方案各有年齡限制。請填實際受補助者的年齡。', options: ['未滿 18 歲', '18～未滿 25 歲', '25～未滿 30 歲', '30～未滿 65 歲', '65 歲以上'] },
 { key: 'residence', title: '你的戶籍地與目前居住地是什麼情況？', why: '地方補助可能分別限制戶籍、居住地與設籍年限，不能只靠目前住處判斷。', options: ['戶籍與居住地在同一縣市，設籍未滿半年', '戶籍與居住地在同一縣市，設籍已滿半年', '戶籍與居住地在不同縣市', '在臺居住，但沒有臺灣戶籍', '不確定戶籍或設籍時間'] },
 { key: 'education', title: '你目前的在學狀態是？', why: '學制會影響獎助學金資格與金額；特定方案還需要確認年級、成績及修業狀態。', options: ['目前未在學', '國小或國中', '高中職或五專前三年', '大學、二專或五專後兩年', '碩士班或博士班'] },
 { key: 'economy', title: '你目前的家庭經濟狀況符合哪一項？', why: '經濟條件影響助學、生活與住宅補助。沒有低收入戶證明，也可能符合其他收入或清寒條件。', options: ['已取得低收入戶資格', '已取得中低收入戶資格', '沒有上述資格，但家庭經濟困難', '沒有上述資格，目前經濟大致穩定', '不清楚家庭經濟資料或認定狀態'] },
 { key: 'identity', title: '你或家庭成員是否具有以下身分？', why: '特定身分有專屬方案；後續仍須確認是本人或家人，以及相關證明。', multi: true, options: ['原住民', '本人或家庭成員持有身心障礙證明', '單親家庭，或經認定的特殊境遇家庭', '其他特定身分，例如僑生、榮民子女、軍公教遺族或客家身分', '以上皆無／不確定'] },
 { key: 'employment', title: '你目前的工作狀態是？', why: '失業、職訓與就業方案條件不同，也需考慮同時就學與工作的人。', multi: true, options: ['受僱工作中，包含兼職', '自營工作或接案', '待業中，正在找工作', '正在參加職業訓練', '目前未工作，也未求職'] },
 { key: 'housing', title: '你目前的居住方式是？', why: '租屋、宿舍、自有住宅與機構住宿對應不同方案；租屋不等於符合無自有住宅條件。', options: ['租屋，包含整戶或分租', '學校宿舍', '自己或配偶持有的住宅', '與親友同住或借住', '機構住宿、無固定住所或其他情況'] },
 { key: 'support', title: '你或家人目前是否有以下需要支援的情況？', why: '育兒、照顧與突發變故可能觸發額外支援，僅問收入與年齡容易漏掉。', multi: true, options: ['懷孕、育兒，或扶養未成年子女', '家人需要協助進食、洗澡、行動等日常生活', '本人因照顧家人而減少工作或無法工作', '最近遭遇重病、事故、災害或主要經濟來源中斷', '以上皆無／不確定'] },
 { key: 'benefits', title: '你目前有領取或正在申請其他補助嗎？', why: '部分同類補助不能併領，需再核對名稱、期間及申請狀態，不能因領過補助就一律排除。', multi: true, options: ['學費減免、助學金或獎學金', '失業給付、職訓津貼或就業補助', '租金或其他住宅補助', '生活、育兒、身障或長照相關補助', '沒有／不確定'] },
];
export const AGE_RANGES = [[0, 17], [18, 24], [25, 29], [30, 64], [65, Infinity]];
export function ageLabel(profile: Profile) {
 return profile.age != null ? `${profile.age} 歲` : profile.screening?.age?.[0] || '年齡未填';
}
export function selectAnswer(current: string[], question: Question, value: string) {
 if (!question.multi) return [value];
 const exclusive = question.key === 'needs' ? undefined : question.options[4];
 if (current.includes(value)) return current.filter(item => item !== value);
 if (value === exclusive) return [value];
 return [...current.filter(item => item !== exclusive), value];
}
export function profileTags(answers: Record<string, string[]>) {
 const has = (key: string, index: number) => answers[key]?.includes(QUESTIONS.find(q => q.key === key)!.options[index]);
 const identities: string[] = [];
 if (answers.education?.length && !has('education', 0)) identities.push('學生');
 if (has('employment', 2)) identities.push('待業／失業');
 if (has('employment', 1)) identities.push('非典型就業');
 if (has('housing', 0)) identities.push('租屋族');
 if (has('support', 0)) identities.push('育兒家庭');
 if (has('age', 4)) identities.push('高齡長者');
 const needs = [['就學與學費'], ['就業與職訓'], ['住宅與租金'], ['經濟補助', '育兒與托育', '生活物資'], ['醫療與健保', '長照與照顧', '身心健康支持']].flatMap((tags, index) => has('needs', index) ? tags : []);
 const economy = ['低收入戶', '中低收入戶', '近貧／經濟不穩定', '一般家庭', '不確定'][QUESTIONS[4].options.indexOf(answers.economy?.[0])];
 return { identities, needs, economy: economy || '不確定' };
}
