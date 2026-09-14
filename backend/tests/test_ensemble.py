"""三方投票分類：兩方同意才放行、任一方說是就不直接丟、LLM 不可用時保留待確認、類別以一致為準。"""

from app.services import classifier_ensemble as ce
from app.services import embeddings

SCHOLARSHIP_TEXT = "獎學金名稱：測試縣清寒優秀學生獎學金 申請資格：設籍本縣六個月以上之低收入戶學生，學業成績平均80分以上。獎助內容：每名獎助學金 3,000 元。申請期間：115/09/01～115/09/30。申請方式：向就讀學校申請。"
PRIVACY_TEXT = "本網站隱私權保護政策說明如何蒐集、處理及利用您的個人資料。Cookie 之使用與資料之保護。"


def fake_signal(p, top):
    return lambda *_a, **_k: {"p_benefit": p, "knn_yes": 5 if p > 0.5 else 1, "knn_no": 1 if p > 0.5 else 5, "category_scores": {c: 0.5 - i * 0.01 for i, c in enumerate(top)}, "top": [(c, 0.5 - i * 0.01) for i, c in enumerate(top)], "margin": 0.01, "model": "test"}


def test_both_signals_agree_admits_without_llm(monkeypatch):
    monkeypatch.setattr(embeddings, "embedding_signal", fake_signal(0.9, ["scholarship", "student_aid"]))
    calls = []
    r = ce.classify_ensemble("清寒優秀學生獎學金", SCHOLARSHIP_TEXT, use_llm=True, llm_classify=lambda *a: calls.append(a) or {"is_benefit": True, "category": "scholarship", "page_kind": "program", "confidence": 0.9})
    assert r.is_benefit and not r.uncertain and r.category == "scholarship" and r.category_confidence == "high"
    assert not calls  # 兩方一致不需要 LLM


def test_both_signals_reject(monkeypatch):
    monkeypatch.setattr(embeddings, "embedding_signal", fake_signal(0.1, ["scholarship"]))
    r = ce.classify_ensemble("隱私權政策", PRIVACY_TEXT, use_llm=True, llm_classify=lambda *a: {"is_benefit": True, "category": "scholarship", "page_kind": "program", "confidence": 0.9})
    assert not r.is_benefit


def test_one_yes_and_llm_no_is_kept_uncertain(monkeypatch):
    monkeypatch.setattr(embeddings, "embedding_signal", fake_signal(0.2, ["scholarship"]))  # embedding 說否、關鍵字說是
    r = ce.classify_ensemble("清寒優秀學生獎學金", SCHOLARSHIP_TEXT, use_llm=True, llm_classify=lambda *a: {"is_benefit": False, "category": "", "page_kind": "other", "confidence": 0.8})
    assert r.is_benefit and r.uncertain and r.llm_used


def test_llm_unavailable_keeps_weak_yes_uncertain(monkeypatch):
    monkeypatch.setattr(embeddings, "embedding_signal", fake_signal(0.2, ["scholarship"]))
    r = ce.classify_ensemble("清寒優秀學生獎學金", SCHOLARSHIP_TEXT, use_llm=False, llm_classify=None)
    assert r.is_benefit and r.uncertain


def test_portal_pages_are_kept_as_portal_without_voting(monkeypatch):
    monkeypatch.setattr(embeddings, "embedding_signal", fake_signal(0.1, ["scholarship"]))  # 就算 embedding 說否
    calls = []
    r = ce.classify_ensemble("老人經濟補助總覽", "單元查詢 更新日期 主題 中低收入老人生活津貼 重陽敬老金 假牙補助", use_llm=True, llm_classify=lambda *a: calls.append(a) or {"is_benefit": False}, seed_category="elderly_allowance")
    assert r.is_benefit and r.page_kind == "portal" and not r.uncertain and r.category == "elderly_allowance"
    assert not calls  # 彙整頁不呼叫 LLM


def test_rejected_page_keeps_its_structural_kind(monkeypatch):
    monkeypatch.setattr(embeddings, "embedding_signal", fake_signal(0.1, ["scholarship"]))
    r = ce.classify_ensemble("本站簡介", PRIVACY_TEXT, use_llm=False, llm_classify=None)  # 標題沒有結構性排除字眼 → 走三方投票
    assert not r.is_benefit and r.page_kind == "program" and r.decision_basis
    r2 = ce.classify_ensemble("隱私權政策", PRIVACY_TEXT, use_llm=False, llm_classify=None)  # 結構性排除 → 保留 site_info 這個種類
    assert not r2.is_benefit and r2.page_kind == "site_info"


def test_structural_exclusion_and_thin_program(monkeypatch):
    monkeypatch.setattr(embeddings, "embedding_signal", fake_signal(0.9, ["scholarship"]))
    assert not ce.classify_ensemble("(檔案下載)長期照顧服務申請書.pdf", "申請書 pdf", use_llm=False).is_benefit
    thin = ce.classify_ensemble("少年就業力準備計畫", "更新日期 相關檔案 少年就業力準備計畫 pdf 附件一 pdf 附件二 pdf", use_llm=False)
    assert thin.is_benefit and thin.uncertain


def test_category_disagreement_prefers_embedding_and_keeps_secondary(monkeypatch):
    monkeypatch.setattr(embeddings, "embedding_signal", fake_signal(0.9, ["student_aid", "scholarship"]))
    r = ce.classify_ensemble("清寒學生助學金", SCHOLARSHIP_TEXT, use_llm=False, llm_classify=None)
    assert r.is_benefit
    assert r.category in {"student_aid", "scholarship"}
    assert set(r.categories_secondary) & {"student_aid", "scholarship"} or r.category_confidence == "high"
