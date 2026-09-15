from app.matching import guidance as module
import pytest


@pytest.fixture(autouse=True)
def no_search_network(monkeypatch):
    monkeypatch.setattr('app.api.assistant_search.search_for_assistant', lambda data: (None, None))

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


def test_saved_needs_survive_other_answers_and_unsure_scope_is_not_repeated(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    monkeypatch.setattr(module, 'load_records', lambda db: [])
    start = module.guidance({'_domains': ['education', 'housing', 'labor']}, '', '')
    assert start['question'] is None
    answer = module.guidance(start['profile'], '有身心障礙，也需要醫療', 'identity.has_disability')
    assert answer['profile']['_domains'] == ['education', 'housing', 'labor']
    skipped = module.guidance({}, '不確定', 'guidance.scope')
    assert skipped['question'] is None
    resumed = module.guidance(skipped['profile'], '不知道', '')
    assert resumed['question'] is None
    assert resumed['profile']['_scope_skipped'] is True


def test_grouped_education_rejects_incompatible_levels_without_guessing():
    from app.matching import Profile, MatchingEngine
    from app.matching.rule_engine import evaluate_rule
    profile = Profile.from_dict({'attributes': {'applicant.age': 20, 'applicant.is_student': True},
                                 'preferences': {'enum_candidates': {'education.level': ['university', 'junior_college']}}})
    rule = {'id': 'education', 'attribute_id': 'education.level', 'group_id': 'education', 'operator': 'in',
            'value': ['elementary', 'junior_high'], 'complexity': 'simple', 'confidence': 1, 'inferred': False}
    assert MatchingEngine().match_one({'_id': 'child-aid', 'rules': [rule]}, profile).status == 'not_match'
    assert evaluate_rule({**rule, 'value': ['university']}, profile).status == 'unknown'
    assert evaluate_rule({**rule, 'value': ['university', 'junior_college']}, profile).status == 'match'
    profile.set('education.level', 'university')
    assert evaluate_rule({**rule, 'value': ['university']}, profile).status == 'match'
