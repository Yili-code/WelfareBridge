"""API 端對端（需要本機 MongoDB）：fixture 官方頁面 → pipeline → REST。"""

PROFILE = {"attributes": {"education.level": "university", "education.grade": 2, "residence.household_city": "基隆市", "academic.average_score": 82}, "need_type": "cash_now"}


def test_health_and_stats(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["database"] == "ok"
    stats = client.get("/api/stats").json()
    assert stats["benefits_total"] >= 1 and stats["raw_documents_total"] >= 1
    assert stats["registry"]["attributes"] >= 70


def test_list_detail_and_rules(client):
    body = client.get("/api/benefits", params={"application_status": "all", "canonical_only": False}).json()
    assert body["total"] >= 1
    item = next(i for i in body["items"] if i["source_id"] == "helpdreams_gov")
    assert item["source_url"].startswith("https://www.edu.tw/") and item["source_verified"] is True
    assert "高雄市" in item["residence_cities"]
    assert isinstance(item["uncertain"], bool) and isinstance(item["category_uncertain"], bool) and item["classification_basis"]  # 清單投影要留住三方投票旗標
    detail = client.get(f"/api/benefits/{item['id']}").json()
    assert detail["raw_document"]["raw_text"].startswith("獎學金名稱")
    assert detail["raw_document"]["content_hash"]
    rules = detail["rules"]
    assert any(r["attribute_id"] == "academic.average_score" and r["value"] == 80 for r in rules)
    assert all(r["evidence"]["excerpt"] for r in rules)
    assert any(r["attribute_id"] == "residence.household_city" and r["value"] == ["高雄市"] for r in rules)
    raw = client.get(f"/api/benefits/{item['id']}/raw").json()
    assert "<div" in raw["raw_html"]


def test_registry_and_options(client):
    registry = client.get("/api/registry").json()
    assert any(a["id"] == "care.cms_level" for a in registry["attributes"])
    options = client.get("/api/meta/options").json()
    assert "catalog" in options and "residence.household_city" in options["catalog"]
    assert any(n["value"] == "cash_now" for n in options["need_types"])


def test_matching_flow(client):
    body = client.post("/api/matching", json={"profile": PROFILE, "include_expired": True, "use_llm": False}).json()
    assert body["disclaimer"].startswith("以上為系統依官方公告內容進行的初步資格比對")
    assert body["summary"]["total"] >= 1
    kaohsiung = next(m for m in body["matches"] if m["title"].startswith("高雄市115"))
    assert kaohsiung["status"] == "not_match"
    assert any(c["attribute_id"] == "residence.household_city" for c in kaohsiung["failed_conditions"])
    assert body["profile_id"] and "ranking" in body


def test_profile_parse_questions_and_feedback(client):
    parsed = client.post("/api/profile/parse", json={"text": "我是高雄人，大二，平均85分，低收入戶", "use_llm": False}).json()
    attributes = parsed["profile"]["attributes"]
    assert attributes["residence.household_city"]["value"] == "高雄市"
    questions = client.post("/api/profile/questions", json={"profile": parsed["profile"], "mode": "dynamic", "max_questions": 3}).json()
    assert "questions" in questions and "candidate_count" in questions
    step = client.post("/api/profile/questions", json={"profile": {}, "mode": "step", "max_questions": 1}).json()
    assert step["questions"] and step["questions"][0]["attribute_id"]
    match = client.post("/api/matching", json={"profile": parsed["profile"], "include_expired": True, "use_llm": False}).json()
    kaohsiung = next(m for m in match["matches"] if m["title"].startswith("高雄市115"))
    assert kaohsiung["status"] in {"possible_match", "high_match"}
    feedback = client.post("/api/feedback", json={"benefit_id": kaohsiung["benefit_id"], "profile_id": match["profile_id"], "event": "applied"}).json()
    assert feedback["ok"] is True
    assert client.get("/api/crawler/status").json()["sources"]
    assert client.get("/api/sources").status_code == 200
    assert client.get("/api/keywords").json()["table"]


def test_search_api_matches_list_filters(client):
    params = {"keyword": "高雄市", "application_status": "all"}
    search = client.get("/api/benefits/search", params=params)
    listing = client.get("/api/benefits", params=params)
    assert search.status_code == listing.status_code == 200
    assert search.json()["total"] > 0
    assert [item["id"] for item in search.json()["items"]] == [item["id"] for item in listing.json()["items"]]