"use client";

import { useState } from "react";
import { REGIONS } from "@/lib/options";
import { updateProfile } from "@/lib/store";
import type { AssistantAttribute, Profile } from "@/lib/types";
import type { QuickQuestion } from "./api";
import { answerQuestion } from "./assistant-memory";

/** 有些問題的「不適用」要寫到另一個欄位：沒有子女時記子女人數 0，含子女年齡條件的補助才會判為不符 */
const NOT_APPLICABLE: Record<string, { label: string; attributeId: string; entry: Omit<AssistantAttribute, "updatedAt"> }> = {
  "family.youngest_child_age": { label: "沒有未成年子女", attributeId: "family.children_count", entry: { label: "子女人數", type: "number", unit: "人", value: 0, valueLabel: "0 人", source: "edited" } },
};

function NumberAnswer({ question, onAnswer }: { question: QuickQuestion; onAnswer: (raw: string) => void }) {
  const [value, setValue] = useState("");
  return <form className="qq-number" onSubmit={e => { e.preventDefault(); if (value !== "") onAnswer(value); }}>
    <label className="sr" htmlFor={`wui-qq-${question.attribute_id}`}>{question.label}</label>
    <input id={`wui-qq-${question.attribute_id}`} type="number" inputMode="numeric" min={0} value={value} onChange={e => setValue(e.target.value)} placeholder="請輸入數字" />
    {question.unit && <span>{question.unit}</span>}
    <button type="submit" className="btn sm" disabled={value === ""}>確定</button>
  </form>;
}

/** 「補這幾題，就能確認更多補助」：回答直接寫進資料卡，主畫面重新比對 */
export default function QuickQuestions({ profile, questions, onSaved }: { profile: Profile; questions: QuickQuestion[]; onSaved: (message: string) => void }) {
  if (!questions.length) return null;
  const save = (question: QuickQuestion, raw: string) => {
    const entry = answerQuestion(question, raw);
    updateProfile(profile.id, { assistantAttributes: { ...profile.assistantAttributes, [question.attribute_id]: entry } });
    onSaved(raw === "" ? `已記下「${question.label}」不確定，之後不會再問` : `已把「${question.label}：${entry.valueLabel}」加入資料卡，正在重新比對`);
  };
  const notApplicable = (question: QuickQuestion) => {
    const option = NOT_APPLICABLE[question.attribute_id];
    updateProfile(profile.id, { assistantAttributes: { ...profile.assistantAttributes, [option.attributeId]: { ...option.entry, updatedAt: new Date().toISOString() } } });
    onSaved(`已記下「${option.label}」，正在重新比對`);
  };

  return <section className="box quickq" aria-labelledby="wui-quickq-title">
    <h2 id="wui-quickq-title">補這幾題，就能確認更多補助</h2>
    <p className="hint">這些是「需要進一步確認」的補助最常缺的資料。點選答案就會寫進資料卡並重新比對，不必開小幫手。</p>
    <ol className="qq-list">
      {questions.map(question => <li key={question.attribute_id} className="qq">
        <p className="qq-q">{question.question}<small>有 {question.affected} 項補助需要這項資料{question.help ? `・${question.help}` : ""}</small></p>
        <div className="qq-a">
          {question.type === "number" ? <NumberAnswer question={question} onAnswer={raw => save(question, raw)} />
            : question.type === "city" ? <select aria-label={question.label} defaultValue="" onChange={e => { if (e.target.value) save(question, e.target.value); }}>
              <option value="" disabled>請選擇縣市</option>{REGIONS.map(city => <option key={city}>{city}</option>)}
            </select>
            : question.options.length > 8 ? <select aria-label={question.label} defaultValue="" onChange={e => { if (e.target.value) save(question, e.target.value); }}>
              <option value="" disabled>請選擇</option>{question.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            : question.options.map(option => <button key={option.value} type="button" className="chip" onClick={() => save(question, option.value)}>{option.label}</button>)}
          {NOT_APPLICABLE[question.attribute_id] && <button type="button" className="chip" onClick={() => notApplicable(question)}>{NOT_APPLICABLE[question.attribute_id].label}</button>}
          <button type="button" className="skip" onClick={() => save(question, "")}>不確定</button>
        </div>
      </li>)}
    </ol>
  </section>;
}
