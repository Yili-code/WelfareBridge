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


def test_education_question_only_offers_levels_inside_the_card_range(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    rule = {'id': 'e', 'attribute_id': 'education.level', 'group_id': 'education', 'operator': 'in', 'value': ['university'], 'complexity': 'simple', 'confidence': 1, 'inferred': False}
    monkeypatch.setattr(module, 'load_records', lambda db: [{'_id': 'u', 'domain': 'education', 'rules': [rule]}])
    data = {'attributes': {'applicant.age': 20, 'applicant.is_student': True}, '_domains': ['education'],
            'preferences': {'enum_candidates': {'education.level': ['university', 'junior_college']}}}
    question = module.guidance(data, '', '')['question']
    assert question['attribute_id'] == 'education.level'
    assert {o['value'] for o in question['options']} == {'university', 'junior_college'}


@pytest.mark.parametrize('text,domains', [
    ('我媽媽失智需要人照顧，我得減少工作', {'long_term_care'}),
    ('我是單親，要養兩個小孩，最近家裡出事缺錢', {'social_welfare'}),
    ('我被裁員三個月了', {'labor'}),
    ('我想買房子', {'housing'}),
])
def test_everyday_wording_picks_the_benefit_area(monkeypatch, text, domains):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    monkeypatch.setattr(module, 'load_records', lambda db: [])
    result = module.guidance({}, text, '')
    assert domains <= set(result['profile']['_domains'])


def test_layoff_and_no_labor_insurance_are_read_from_free_text():
    from app.matching import parse_profile_text
    profile, parsed, _ = parse_profile_text('我被裁員三個月了，沒有勞保，住台北')
    values = {p['attribute_id']: p['value'] for p in parsed}
    assert values['employment.status'] == 'unemployed'
    assert values['employment.involuntary_separation'] is True
    assert values['financial.labor_insured'] is False


def test_colloquial_yes_no_and_number_answers_are_understood(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    monkeypatch.setattr(module, 'load_records', lambda db: [])
    base = {'_domains': ['housing']}
    assert module.guidance(base, '沒有喔', 'identity.low_income')['profile']['attributes']['identity.low_income']['value'] is False
    assert module.guidance(base, '對', 'identity.low_income')['profile']['attributes']['identity.low_income']['value'] is True
    assert module.guidance(base, '每個月約 8,000 元', 'housing.rent_month')['profile']['attributes']['housing.rent_month']['value'] == 8000
    assert module.guidance(base, '蛤', 'identity.low_income')['not_understood'] is True
    assert module.guidance(base, '不確定', 'identity.low_income')['not_understood'] is False


def test_hedged_and_third_party_answers():
    assert module.yes_no('應該有吧') is module.UNSURE
    assert module.yes_no('還在申請中') is module.UNSURE
    assert module.yes_no('沒有喔') is False
    assert module.yes_no('有，領有身障手冊') is True
    assert module.yes_no('我朋友有') is None
    assert module.yes_no('蛤') is None


def test_unsure_hedge_is_recorded_as_unsure(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    monkeypatch.setattr(module, 'load_records', lambda db: [])
    result = module.guidance({'_domains': ['housing']}, '應該有吧', 'identity.low_income')
    assert result['profile']['attributes']['identity.low_income']['source'] == 'unsure'
    assert result['not_understood'] is False


def test_hedged_answers_to_choice_and_number_questions_skip_the_question(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    monkeypatch.setattr(module, 'load_records', lambda db: [])
    base = {'_domains': ['housing']}
    for attribute, text in [('housing.tenure', '不太確定'), ('housing.rent_month', '不知道'), ('applicant.age', '我不清楚')]:
        result = module.guidance(base, text, attribute)
        assert result['profile']['attributes'][attribute]['source'] == 'unsure'
        assert result['not_understood'] is False


def test_school_year_is_not_read_as_an_age_or_amount(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    monkeypatch.setattr(module, 'load_records', lambda db: [])
    result = module.guidance({'_domains': ['education']}, '大三', 'applicant.age')
    assert 'applicant.age' not in result['profile']['attributes'] or result['profile']['attributes']['applicant.age']['value'] != 3


def test_search_splits_a_sentence_into_need_words():
    from app.api.benefits import _need_terms
    assert _need_terms('租屋') == []
    assert {'失智', '照顧'} <= set(_need_terms('我媽媽失智需要人照顧'))
    assert '日間照顧' in _need_terms('老人 日間照顧')


def test_a_sentence_about_another_need_changes_the_area_instead_of_failing_the_pending_question(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    monkeypatch.setattr(module, 'load_records', lambda db: [])
    result = module.guidance({'_domains': ['education']}, '其實我想找長照服務，我媽媽失智，我得減少工作', 'academic.average_score')
    assert result['profile']['_domains'] == ['long_term_care']
    assert result['not_understood'] is False


def test_second_unreadable_answer_to_the_same_question_skips_it(monkeypatch):
    monkeypatch.setattr(module, 'get_db', lambda: None)
    rule = {'id': 'c', 'attribute_id': 'residence.household_city', 'group_id': 'residence', 'operator': '=', 'value': '臺北市', 'complexity': 'simple', 'confidence': 1, 'inferred': False}
    monkeypatch.setattr(module, 'load_records', lambda db: [{'_id': 'c', 'domain': 'housing', 'rules': [rule]}])
    first = module.guidance({'_domains': ['housing']}, '30', 'residence.household_city')
    assert first['not_understood'] is True and first['question']['attribute_id'] == 'residence.household_city'
    second = module.guidance(first['profile'], '30', 'residence.household_city')
    assert second['skipped_target'] == 'residence.household_city' and second['not_understood'] is False
    assert second['question'] is None or second['question']['attribute_id'] != 'residence.household_city'


@pytest.mark.parametrize('text,attribute,expected', [
    ('30000元', 'household.income_year', 30000), ('約 8,000 元', 'housing.rent_month', 8000), ('四萬', 'housing.rent_month', 40000),
    ('一萬二', 'housing.rent_month', 12000), ('3.5萬', 'household.income_year', 35000), ('半年', 'residence.duration_months', 6),
    ('兩年三個月', 'residence.duration_months', 27), ('3年', 'residence.duration_months', 36), ('二十一歲', 'applicant.age', 21), ('不知道', 'applicant.age', None),
])
def test_spoken_numbers(text, attribute, expected):
    assert module.parse_number(text, attribute) == expected


def test_follow_ups_skip_questions_whose_premise_was_ruled_out():
    from app.matching import Profile
    from app.registry import get_registry
    registry = get_registry()
    profile = Profile.from_dict({'attributes': {'disability.has_certificate': False, 'applicant.is_student': False, 'employment.status': 'employed'}}, registry)
    assert module.blocked('disability.certificate_level', profile, registry)
    assert module.blocked('academic.average_score', profile, registry)
    assert module.blocked('employment.unemployed_months', profile, registry)
    assert not module.blocked('applicant.age', profile, registry)


def test_low_income_household_is_not_asked_about_middle_low_income():
    from app.matching import Profile
    from app.registry import get_registry
    registry = get_registry()
    assert module.blocked('identity.middle_low_income', Profile.from_dict({'attributes': {'identity.low_income': True}}, registry), registry)
    assert not module.blocked('identity.middle_low_income', Profile.from_dict({'attributes': {'identity.low_income': False}}, registry), registry)
