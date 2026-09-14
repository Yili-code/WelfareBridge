from app.api import diagnostics

def test_diagnosis_includes_rejected_and_unprocessed_records(monkeypatch):
    records = [
        {"_id": "age", "title": "高齡補助", "is_canonical": True, "rules": [{"id": "r", "attribute_id": "applicant.age", "operator": ">=", "value": 65, "group_id": "applicant_age", "complexity": "simple", "confidence": 1, "inferred": False}]},
        {"_id": "empty", "title": "未處理公告", "classification": {"uncertain": True}, "rules": []},
    ]
    class Collection:
        def count_documents(self, query): return len(records)
        def find(self, query): return self
        def sort(self, *args): return self
        def limit(self, n): return records
    class DB:
        benefits = Collection()
    monkeypatch.setattr(diagnostics, "get_db", lambda: DB())
    result = diagnostics.diagnose(diagnostics.DiagnosticRequest(profile={"attributes": {"applicant.age": 22}}))
    assert result['items'][0]['status'] == 'not_match'
    assert result['items'][0]['failed_conditions'][0]['user_value'] == 22
    assert result['items'][1]['rule_count'] == 0
    assert '補助分類尚待確認' in result['items'][1]['retrieval_exclusions']
    result = diagnostics.diagnose(diagnostics.DiagnosticRequest(profile={"attributes": {}}))
    assert result['items'][0]['status'] == 'insufficient_data'
    assert result['items'][0]['missing_conditions'][0]['user_value'] is None
