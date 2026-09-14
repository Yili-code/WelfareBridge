"""Crawler framework：所有官方來源爬蟲都繼承 benefit_crawler.base.base_crawler.BaseCrawler。

目錄：
    base/        BaseCrawler、PoliteHttpClient（retry / backoff / robots / rate limit）、SourceValidator、parser
    government/  中央政府（教育部圓夢助學網、原住民族委員會、青年發展署…）
    local/       地方政府（基隆市政府教育處、臺北市政府教育局…）
    township/    區／鄉／鎮公所（設定檔驅動）
    school/      學校官方網站（provider_type = school）
    config/      sources.yaml、official_domains.yaml、keyword_rules.yaml

執行：python -m benefit_crawler --help
"""
