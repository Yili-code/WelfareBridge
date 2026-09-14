"""分類器信心值：類別證據太弱時不能因為「沒有第二名」就拿滿分（否則跳過本地 AI 二次判斷）。"""

import yaml

from app.services.classifier import BenefitClassifier


def make_classifier(tmp_path):
    rules = {
        "version": 2,
        "benefit_signal": {
            "threshold": 4,
            "title_bonus": 2,
            "keywords": [{"term": "補助", "weight": 5}, {"term": "申請資格", "weight": 5}, {"term": "檢附", "weight": 3}],
            "negative": [{"term": "隱私權政策", "weight": -3}],
        },
        "categories": {
            "scholarship": {"label": "獎學金", "keywords": [{"term": "獎學金", "weight": 4}, {"term": "成績", "weight": 3}]},
            "disability_other": {"label": "身心障礙其他福利", "keywords": [{"term": "福利", "weight": 1}]},
        },
    }
    path = tmp_path / "rules.yaml"
    path.write_text(yaml.safe_dump(rules, allow_unicode=True), encoding="utf-8")
    return BenefitClassifier(path)


def test_single_weak_category_hit_stays_uncertain(tmp_path):
    clf = make_classifier(tmp_path)
    result = clf.classify("所屬網站介紹", "本局各項福利服務網站介紹。申請資格與補助請檢附文件。")
    assert result.is_benefit
    assert result.category == "disability_other"
    assert result.confidence < 0.75, result.confidence  # 交給本地 AI 二次判斷，而不是直接當補助


def test_strong_category_is_confident(tmp_path):
    clf = make_classifier(tmp_path)
    result = clf.classify("清寒獎學金", "獎學金申請資格：成績 80 分以上，檢附證明文件，補助每名一萬元。")
    assert result.is_benefit and result.category == "scholarship"
    assert result.confidence >= 0.75, result.confidence


def test_negative_and_listing_page(tmp_path):
    clf = make_classifier(tmp_path)
    result = clf.classify("最新消息", "共 62 筆資料，每頁顯示 20 筆。補助 補助 申請資格 獎學金")
    assert "列表頁分頁標記" in result.matched_negative
    assert not clf.classify("隱私權政策", "隱私權政策 補助").is_benefit
