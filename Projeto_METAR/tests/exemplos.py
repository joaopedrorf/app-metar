"""Respostas de exemplo das APIs, no formato que CheckWX e AISWEB devolvem."""

METAR_SBGL = {
    "icao": "SBGL",
    "raw_text": "METAR SBGL 191800Z 16012G22KT 9999 -RA BKN015 OVC030 22/19 Q1014",
    "visibility": {"meters": "10000"},
    "ceiling": {"feet": 1500},
    "wind": {"degrees": 160, "speed_kts": 12, "gust_kts": 22},
    "barometer": {"hpa": 1014},
    "conditions": [{"code": "-RA", "text": "Light Rain"}],
}

TAF_SBGL = {
    "icao": "SBGL",
    "raw_text": "TAF SBGL 191630Z 1918/2024 16010KT 9999 BKN020 "
                "TEMPO 1921/2001 4000 RA BKN010 BECMG 2006/2008 VRB03KT",
    "forecast": [
        {
            "timestamp": {"from": "2026-10-19T18:00:00", "to": "2026-10-21T00:00:00"},
            "wind": {"degrees": 160, "speed_kts": 10},
            "visibility": {"meters": "10000"},
            "clouds": [{"code": "BKN", "feet": 2000}],
        },
        {
            "timestamp": {"from": "2026-10-19T21:00:00", "to": "2026-10-20T01:00:00"},
            "change": {"indicator": {"code": "TEMPO", "text": "Temporarily"}},
            "visibility": {"meters": "4000"},
            "clouds": [{"code": "BKN", "feet": 1000}],
            "conditions": [{"code": "RA", "text": "Rain"}],
        },
        {
            "timestamp": {"from": "2026-10-20T06:00:00", "to": "2026-10-20T08:00:00"},
            "change": {"indicator": {"code": "BECMG", "text": "Becoming"}},
            "wind": {"speed_kts": 3},
        },
    ],
}

NOTAM_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<aisweb>
  <notam total="2">
    <item>
      <id>123</id>
      <n>C1234/26</n>
      <loc>SBGL</loc>
      <b>2610150900</b>
      <c>2611152359 EST</c>
      <e>RWY 10/28 CLSD PARA POUSO E DECOLAGEM</e>
    </item>
    <item>
      <id>124</id>
      <n>C1300/26</n>
      <loc>SBGL</loc>
      <b>2610010000</b>
      <c>PERM</c>
      <d>SEG A SEX 1000-1800</d>
      <e>TWY B INTERDITADA</e>
    </item>
  </notam>
</aisweb>"""
