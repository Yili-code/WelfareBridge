"""教育部開放資料（政府資料開放平臺）匯入與「附近教育資源」API。"""
from app.config import Settings
from app.services import moe_opendata


def test_import_is_idempotent_and_resources_api_reports_dataset_source(db, client, monkeypatch, tmp_path):
    folder = tmp_path / "opendata" / "moe"
    folder.mkdir(parents=True)
    (folder / "leling.csv").write_text(
        "序號,縣市代碼,縣市,鄉鎮市區名稱,承辦單位,樂齡中心名稱,中心電話,中心傳真,中心地址\n"
        "1,10017,基隆市,中山區,某協會,基隆市中山區樂齡學習中心,02-1,02-2,基隆市中山區中華路42號\n", encoding="utf-8-sig")
    monkeypatch.setattr(Settings, "data_path", property(lambda self: tmp_path))
    db.providers.delete_many({"source_id": {"$regex": "^moe_od_"}})
    try:
        assert moe_opendata.import_moe_opendata() == {"moe_od_163769": 1}
        assert moe_opendata.import_moe_opendata() == {"moe_od_163769": 1}  # 重跑不會重複
        data = client.get("/api/public/resources", params={"city": "基隆", "kind": "樂齡學習中心"}).json()
        assert data["city"] == "基隆市" and data["total"] == 1 and data["items"][0]["name"].endswith("樂齡學習中心")
        assert data["items"][0]["source_url"] == "https://data.gov.tw/dataset/163769"
        assert any(d["nid"] == 163769 and d["count"] == 1 and "政府資料開放授權條款" in d["license"] for d in data["datasets"])
    finally:
        db.providers.delete_many({"source_id": {"$regex": "^moe_od_"}})
