from benefit_crawler.base.source_validator import SourceValidator


def test_gov_domain_is_verified(validator: SourceValidator):
    result = validator.validate_url("https://www.klcg.gov.tw/tw/education/3473.html")
    assert result.verified is True
    assert result.status == "verified"
    assert result.domain_type == "government"


def test_whitelisted_edu_domain_is_government(validator: SourceValidator):
    result = validator.validate_url("https://www.edu.tw/helpdreams/Grants.aspx")
    assert result.verified is True
    assert result.provider_type == "central_government"
    assert "manual_whitelist" in result.method


def test_public_school_domain_is_school(validator: SourceValidator):
    result = validator.validate_url("https://stu.ntou.edu.tw/p/403-1023-1039-1.php")
    assert result.verified is True
    assert result.provider_type == "school"
    assert result.source_type == "school_site"


def test_unknown_edu_domain_needs_review(validator: SourceValidator):
    result = validator.validate_url("https://www.some-cram-school.edu.tw/scholarship")
    assert result.verified is False
    assert result.status == "needs_review"


def test_non_official_domain_rejected(validator: SourceValidator):
    result = validator.validate_url("https://scholarship-blog.example.com/list")
    assert result.verified is False


def test_http_is_not_verified(validator: SourceValidator):
    result = validator.validate_url("http://www.klcg.gov.tw/tw/education/3473.html")
    assert result.verified is False
    assert any("HTTPS" in reason for reason in result.reasons)


def test_title_metadata_mismatch_downgrades(validator: SourceValidator):
    ok = validator.validate_url("https://www.edu.tw/helpdreams/", expected_title_keywords=["教育部"], page_title="教育部圓夢助學網")
    bad = validator.validate_url("https://www.edu.tw/helpdreams/", expected_title_keywords=["教育部"], page_title="Error 404")
    assert ok.verified is True and ok.title_check is True
    assert bad.verified is False and bad.title_check is False
