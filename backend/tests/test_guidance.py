from app.matching import guidance as module

def test_answers_narrow_candidates_and_unknown_does_not_reject(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    def record(id, value):
        return {'_id': id, 'domain': 'housing', 'rules': [{'id': id, 'attribute_id': 'identity.low_income', 'group_id': 'identity', 'operator': '=', 'value': value, 'complexity': 'simple', 'confidence': 1, 'inferred': False}]}
    monkeypatch.setattr(module, 'load_records', lambda db: [record('yes', True), record('no', False)])
    initial = module.guidance({}, '', '')
    assert initial['question']['attribute_id'] == 'guidance.scope'
    start = module.guidance({}, '房租', '')
    assert start['candidate_count'] == 2
    assert start['question']['attribute_id'] == 'identity.low_income'
    answered = module.guidance(start['profile'], '否', 'identity.low_income')
    assert answered['candidate_count'] == 1
    assert answered['question'] is None
    uncertain = module.guidance(start['profile'], '不確定', 'identity.low_income')
    assert uncertain['candidate_count'] == 2
    assert uncertain['question'] is None
