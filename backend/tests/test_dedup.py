"""去重：同一份公告出現在多個官方來源時共用 canonical_id。"""

from app.services.dedup import canonical_rank, is_duplicate


def test_same_benefit_across_sources_is_duplicate():
    official = {"title": "高雄市115學年度第1學期中等以上學校清寒優秀學生獎學金", "provider": "高雄市政府教育局", "application_end": "2026-10-31", "source_url": "https://www.edu.tw/helpdreams/a"}
    repost = {"title": "【115-1學期-政府】高雄市115學年度第1學期中等以上學校清寒優秀學生獎學金(10月23日止)", "provider": "高雄市政府", "application_end": "2026-10-23", "source_url": "https://stu.ntou.edu.tw/b"}
    duplicate, similarity, reason = is_duplicate(repost, official)
    assert duplicate, reason
    other = {"title": "臺北市115學年度清寒優秀學生獎學金", "provider": "臺北市政府教育局", "application_end": "2026-10-31", "source_url": "https://x"}
    assert not is_duplicate(other, official)[0]
    assert canonical_rank({"data_confidence": 95, "source_type": "government_site", "is_repost": False}) > canonical_rank({"data_confidence": 95, "source_type": "school_site", "is_repost": True})


def test_pipeline_links_ntou_repost_to_helpdreams_canonical(seeded_db):
    rows = list(seeded_db.benefits.find({"title": {"$regex": "高雄市115"}}, {"source_id": 1, "canonical_id": 1, "is_canonical": 1}))
    assert len(rows) >= 2, rows
    canonical_ids = {r["canonical_id"] for r in rows}
    assert len(canonical_ids) == 1
    canonical = next(r for r in rows if r["is_canonical"])
    assert canonical["source_id"] == "helpdreams_gov"


def test_short_title_with_qualifier_is_distinct_program():
    base = {"title": "缺工就業獎勵", "provider": "勞動部勞動力發展署", "application_end": None, "source_url": "https://emps.wda.gov.tw/Internet/Index/labor-shortage.aspx#part-1"}
    special = {"title": "專案缺工就業獎勵", "provider": "勞動部勞動力發展署", "application_end": None, "source_url": "https://emps.wda.gov.tw/Internet/Index/labor-shortage.aspx#part-5"}
    duplicate, _, reason = is_duplicate(special, base)
    assert not duplicate, reason
    disaster = {"title": "天災臨時工作津貼", "provider": "勞動部勞動力發展署", "application_end": None, "source_url": "https://x#part-3"}
    assert not is_duplicate(disaster, {**base, "title": "臨時工作津貼"})[0]
    # 同一頁換個網址參數（?fm=1）仍是同一份
    variant = {**base, "source_url": "https://emps.wda.gov.tw/Internet/Index/labor-shortage.aspx?fm=1#part-1"}
    assert is_duplicate(variant, base)[0]
    # 只差「計畫」等結尾字仍視為同一份
    assert is_duplicate({**base, "title": "缺工就業獎勵計畫"}, base)[0]
