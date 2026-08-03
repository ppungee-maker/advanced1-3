"""Vercel Serverless Function (Python) — POST /api/recommend

프론트에서 {"date": "YYYY-MM-DD"}를 보내면 OpenAI로 여행지를 추천받고,
Kakao Local API로 그 지역 맛집을 검색해 하나의 JSON으로 합쳐 반환한다.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler

import requests
from openai import OpenAI

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
KAKAO_LOCAL_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

FIRST_PROMPT_TEMPLATE = """당신은 국내 여행 추천 전문가입니다. {date} 무렵 한국 국내에서 여행하기 좋은 지역 1곳을 추천하세요.

다음 JSON 형식으로만, 다른 설명 없이 응답하세요:
{{
  "recommended_city": "지역명 (예: 제주, 강릉)",
  "weather": "그 시기 일반적인 날씨 요약",
  "events": ["행사/축제 후보 1~3개"],
  "reason": "추천 근거 2~4문장"
}}"""


def get_first_recommendation(client, date_str):
    """1차 여행지 추천. JSON 파싱 실패 시 1회 재시도, 실패하면 None."""
    prompt = FIRST_PROMPT_TEMPLATE.format(date=date_str)
    required_keys = ("recommended_city", "weather", "events", "reason")

    for _ in range(2):
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            data = json.loads(resp.choices[0].message.content)
            if all(key in data for key in required_keys):
                return data
            prompt += f"\n\n반드시 {', '.join(required_keys)} 키만 포함한 JSON으로 다시 응답하세요."
        except json.JSONDecodeError:
            prompt += "\n\n올바른 JSON 형식이 아니었습니다. 반드시 유효한 JSON만 출력하세요."
        except Exception:
            return None

    return None


def get_restaurants(kakao_key, city, count=5):
    """Kakao Local로 맛집을 검색한다. 실패하면 빈 리스트."""
    try:
        resp = requests.get(
            KAKAO_LOCAL_URL,
            params={"query": f"{city} 맛집", "size": count},
            headers={"Authorization": f"KakaoAK {kakao_key}"},
            timeout=8,
        )
        if resp.status_code in (401, 403):
            return []
        resp.raise_for_status()
        documents = resp.json().get("documents", [])
    except requests.RequestException:
        return []

    return [
        {
            "name": doc.get("place_name"),
            "address": doc.get("road_address_name") or doc.get("address_name"),
            "category": doc.get("category_name"),
            "url": doc.get("place_url"),
        }
        for doc in documents[:count]
    ]


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"

        try:
            body = json.loads(raw_body or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "요청 본문이 올바른 JSON이 아닙니다."})
            return

        date_str = (body.get("date") or "").strip()
        if not date_str:
            self._send_json(400, {"error": "date가 필요합니다."})
            return

        openai_key = os.environ.get("OPENAI_API_KEY")
        kakao_key = os.environ.get("KAKAO_REST_API_KEY")
        if not openai_key or not kakao_key:
            self._send_json(
                500,
                {"error": "서버에 API 키가 설정되지 않았습니다. Vercel 환경 변수를 확인하세요."},
            )
            return

        client = OpenAI(api_key=openai_key)
        first_json = get_first_recommendation(client, date_str)
        if first_json is None:
            self._send_json(502, {"error": "AI 추천 생성에 실패했습니다. 잠시 후 다시 시도해주세요."})
            return

        restaurants = get_restaurants(kakao_key, first_json["recommended_city"])
        first_json["restaurants"] = restaurants
        self._send_json(200, first_json)

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
