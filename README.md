# AI 여행 추천 — 미니 웹 서비스

여행 날짜만 입력하면 AI가 그 시기에 어울리는 국내 여행지와 주변 맛집을 추천해주는
3페이지짜리 반응형 웹 서비스. 프론트는 바닐라 HTML/CSS/JS, 백엔드는 Vercel Serverless
Function(Python)으로 OpenAI + Kakao Local API를 연동한다.

- **배포 URL**: https://advanced1-3.vercel.app
- **서비스 기획서**: [`기획서.md`](./기획서.md)
- **미션 원문**: [`문제.md`](./문제.md)
- **증빙 자료(스크린샷)**: [`captures/`](./captures) — 배포된 사이트의 데스크톱/모바일
  홈 화면, AI 여행 추천 기능 실제 동작(부산·크리스마스 시즌 추천 결과) 화면

## 페이지 구성

| 페이지 | 파일 | 내용 |
|---|---|---|
| 홈 | `index.html` | 서비스 소개, 핵심 가치, CTA |
| 여행 추천 (AI 기능) | `recommend.html` | 날짜 입력 → AI 추천 + 맛집 결과 출력 |
| 소개/사용법 | `about.html` | 사용 방법, 동작 원리, 기술 스택 |

## 프로젝트 구조

```
advanced1-3/
├── index.html, recommend.html, about.html   # 프론트엔드 (바닐라)
├── css/style.css
├── js/main.js         # 공통 네비게이션(모바일 토글, 활성 메뉴 표시)
├── js/recommend.js    # AI 기능 폼 로직 (fetch, 에러/타임아웃 처리)
├── api/recommend.py   # 백엔드 — Vercel Serverless Function (Python)
├── requirements.txt   # 백엔드 파이썬 의존성
├── 기획서.md           # 서비스 기획서
└── 문제.md             # 미션 원문
```

프론트(정적 파일)와 백엔드(`api/`)가 폴더로 명확히 구분되어 있다.

## 기술 스택

- 프론트엔드: HTML / CSS / JavaScript (프레임워크 없음)
- 백엔드: Vercel Serverless Functions (Python, `http.server.BaseHTTPRequestHandler` 기반)
- 외부 API: OpenAI(여행지 추천), Kakao Local(맛집 검색)
- 배포: Vercel (GitHub 저장소 연동 자동 배포)

## 로컬 실행 방법

프론트엔드만 정적으로 확인하려면:

```bash
python3 -m http.server 8123
# http://localhost:8123 접속
```

단, 이 방식으로는 `/api/recommend`(백엔드)가 동작하지 않는다. 백엔드까지 포함해
로컬에서 완전히 재현하려면 Vercel CLI를 쓴다:

```bash
npm i -g vercel
vercel dev
```

`vercel dev`는 프로젝트 루트의 `.env`(아래 환경 변수 참고)를 읽어 `api/recommend.py`를
로컬에서도 서버리스 함수처럼 실행해준다.

## 환경 변수(API 키) 설정 방법

이 서비스는 **OpenAI**(여행지 추천)와 **Kakao Local**(맛집 검색) 두 API 키가 필요하다.
키를 코드에 직접 쓰지 않고, 아래 두 곳에 각각 설정한다.

**로컬 개발용** — 프로젝트 루트에 `.env` 파일 생성 (git에는 올라가지 않음):

```
OPENAI_API_KEY=sk-...
KAKAO_REST_API_KEY=...
```

**배포용** — Vercel 대시보드에서 설정 (`.env`는 배포 서버에 자동으로 올라가지 않기 때문):

1. Vercel 프로젝트 → **Settings** → **Environment Variables**
2. `OPENAI_API_KEY`, `KAKAO_REST_API_KEY` 각각 추가 (Production/Preview 모두 체크)
3. 재배포하면 `api/recommend.py`가 `os.environ`으로 값을 읽는다

키 발급 방법(OpenAI/Kakao)은 이전 미션(A1-2) README에 정리해둔 절차와 동일하다 —
OpenAI는 platform.openai.com에서 결제수단 등록 후 API keys 발급, Kakao는
developers.kakao.com에서 앱 생성 후 REST API 키 발급 + **카카오맵 서비스 활성화(ON)** 필요.

## 배포 방법 (Vercel)

1. 이 저장소를 GitHub에 push (이미 완료)
2. https://vercel.com 로그인 → **Add New... → Project**
3. GitHub 저장소 `advanced1-3` 선택 → Import
4. Framework Preset: **Other** (정적 파일 + `api/` 자동 인식됨, 별도 빌드 설정 불필요)
5. **Environment Variables**에 `OPENAI_API_KEY`, `KAKAO_REST_API_KEY` 입력
6. **Deploy** 클릭 → 배포 완료 후 발급된 `https://*.vercel.app` URL 확인
7. 배포 URL에서 3개 페이지 이동 / 반응형 / AI 기능이 실제로 동작하는지 확인
8. 문제가 있으면 코드 수정 → git push → Vercel이 자동 재배포

## AI 기능 UX 및 실패 처리

`recommend.html`에서 날짜를 선택하면 `js/recommend.js`가 `fetch('/api/recommend')`를
호출한다. 아래 3가지 실패 상황을 모두 사용자에게 안내한다.

| 상황 | 처리 |
|---|---|
| 빈 입력(날짜 미선택) | fetch 호출 전에 차단, "여행 날짜를 선택해주세요" 인라인 메시지 |
| API 오류(4xx/5xx) | "추천을 가져오는 데 실패했어요. 잠시 후 다시 시도해주세요" |
| 지연/타임아웃(12초) | `AbortController`로 강제 중단, "응답이 지연되고 있어요..." 메시지 |

백엔드(`api/recommend.py`)도 OpenAI/Kakao 호출 실패를 각각 처리한다 — Kakao 실패는
빈 맛집 리스트로 계속 진행하고, OpenAI 1차 추천 실패는 502로 응답해 프론트가 위 표의
"API 오류" 메시지를 보여주게 한다.

## 핵심 코드 스니펫

**프론트 → 백엔드 요청 흐름** (`js/recommend.js`):

```javascript
const res = await fetch("/api/recommend", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ date }),
  signal: controller.signal, // AbortController로 타임아웃 처리
});
```

**Vercel Serverless Function (Python)** — `api/recommend.py`가 `BaseHTTPRequestHandler`를
구현하면 Vercel이 이를 `/api/recommend` 엔드포인트로 자동 라우팅한다:

```python
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length) or b"{}")
        date_str = (body.get("date") or "").strip()
        if not date_str:
            self._send_json(400, {"error": "date가 필요합니다."})
            return
        ...
```

**환경 변수로 키를 읽는 부분** (`api/recommend.py`):

```python
openai_key = os.environ.get("OPENAI_API_KEY")
kakao_key = os.environ.get("KAKAO_REST_API_KEY")
if not openai_key or not kakao_key:
    self._send_json(500, {"error": "서버에 API 키가 설정되지 않았습니다. Vercel 환경 변수를 확인하세요."})
    return
```

## 설계 노트 (과제 목표 관련 설명)

**HTML/CSS/JavaScript는 각각 어떤 역할을 하는가?**
HTML(`*.html`)은 페이지의 구조와 콘텐츠(제목, 폼, 버튼 등)를 정의한다. CSS(`css/style.css`)는
그 구조에 시각적 스타일(레이아웃, 색상, 반응형 breakpoint)을 입힌다. JavaScript
(`js/main.js`, `js/recommend.js`)는 사용자 상호작용(폼 제출, 메뉴 토글)과 동적 동작
(API 호출, 결과에 따라 DOM을 다시 그리는 것)을 담당한다 — 셋 중 하나라도 없으면 "보여지긴
하는데 반응은 안 하는" 또는 "동작은 하는데 구조가 없는" 페이지가 된다.

**사용자 입력 → fetch 요청 → 화면 반영 흐름은?**
`recommend.html`의 날짜 `<input>`에 사용자가 값을 넣고 제출하면, `recommend.js`의
`submit` 이벤트 핸들러가 그 값을 읽어 `fetch('/api/recommend', {body: JSON.stringify({date})})`
로 HTTP 요청을 만든다. 서버 응답(JSON)이 오면 `renderResult(data)`가 그 데이터로
`result` 엘리먼트의 `innerHTML`을 새로 구성해 화면에 반영한다. 즉 "DOM 이벤트 → 요청
직렬화 → 네트워크 호출 → 응답 역직렬화 → DOM 갱신"의 순환이다.

**Vercel Serverless Functions란? 프론트가 백엔드(Python)를 호출하는 구조는?**
`api/` 폴더 안의 `.py` 파일 하나하나가 독립적인 서버리스 함수가 되어, 파일명이 곧 경로가
된다(`api/recommend.py` → `/api/recommend`). 요청이 올 때만 실행되고 끝나면 종료되는
방식이라 상시 서버를 띄워둘 필요가 없다. 프론트는 이 경로를 그냥 같은 도메인의 API처럼
`fetch('/api/recommend')`로 호출하면 되고, Vercel이 내부적으로 Python 프로세스를 띄워
`handler` 클래스의 `do_POST`를 실행한 뒤 응답을 돌려준다.

**환경 변수로 API 키를 관리해야 하는 이유는?**
키를 코드에 쓰면 GitHub에 그대로 노출되고, 로컬/배포 환경마다 다른 키를 쓰기도 어렵다.
Vercel의 Environment Variables는 코드와 완전히 분리된 곳에 키를 암호화 보관하고, 함수
실행 시점에만 `os.environ`으로 주입한다 — 저장소에는 `.env`(로컬용, gitignore 대상)도
`.env.example` 같은 값 없는 템플릿도 필요 없이, "이 두 키가 필요하다"는 사실만
README(지금 이 문서)에 문서화하면 된다.

**로컬 환경과 배포 환경의 차이, 배포 후 수정·재배포 흐름은?**
로컬(`python3 -m http.server`)은 정적 파일만 서빙하고 `api/`를 실행할 능력이 없다 —
그래서 `/api/recommend` 호출은 로컬 단순 서버에서는 항상 실패한다(이 저장소 개발 중
실제로 이 상태로 프론트 UI/에러 처리를 검증했다). `vercel dev`나 실제 배포 환경만이
`api/*.py`를 서버리스 함수로 실행한다. 배포 후 버그를 발견하면: 로컬에서 원인 파악 →
코드 수정 → `git push` → Vercel이 GitHub 웹훅으로 감지해 자동 재배포 → 새 배포 URL(또는
같은 프로덕션 URL)에서 재확인하는 흐름을 따른다.

**실제 배포 트러블슈팅 사례** (이 흐름을 그대로 겪은 실제 기록):

1. 첫 배포가 `No python entrypoint found in default locations`로 실패 → Vercel이
   제안한 대로 `pyproject.toml`에 `[tool.vercel] entrypoint = "api.recommend:handler"`
   추가 → `git push` → 재배포
2. 이번엔 `Error: No 'project' table found in pyproject.toml`로 실패(uv가 표준
   `[project]` 메타데이터를 요구) → `[project]` 테이블(name/version/dependencies) 추가
   → 재배포 → 빌드는 성공
3. 그런데 배포된 사이트의 홈(`/`, GET)에 접속하면 `501 Unsupported method ('GET')`
   에러가 떴다 — **정적 파일 요청까지 우리 Python 함수 하나로 몰리고 있었다.** 공식 문서를
   찾아보니 `[tool.vercel] entrypoint`는 "사이트 전체가 하나의 Python 앱(Flask/FastAPI 등)"
   이라는 뜻이라, Framework Preset이 "Python"으로 잡히면서 정적 사이트+개별 api 함수 구조가
   아니라 단일 앱 구조로 오인식된 것이 원인이었다
4. `pyproject.toml`을 완전히 제거하고, 대신 `vercel.json`에 `{"framework": null}`을 추가해
   Framework Preset을 "Other"로 강제 지정 → 재배포 → 정적 파일과 `/api/recommend`가 각각
   정상적으로 분리되어 라우팅됨을 확인
5. 마지막으로 `/api/recommend` 호출 시 "API 키가 설정되지 않았습니다" 에러 확인 → Vercel
   Environment Variables에 등록된 키 이름이 `KAKAO_REST_API_KEY`가 아니라 `Kakao` 등
   잘못된 이름으로 들어가 있었음을 발견 → 삭제 후 정확한 이름으로 재등록 → 재배포 후 실제
   여행지 추천이 정상적으로 동작함을 확인

매 단계마다 "에러 메시지 읽기 → (필요하면 공식 문서로 원인 검증) → 코드/설정 수정 →
재배포 → 실제 배포 URL에서 재확인"을 반복한 것이 이 미션이 요구하는 배포 트러블슈팅
흐름 그 자체였다.

**AI 코딩 도구가 생성한 코드의 오류를 어떻게 파악하고 고치는가?**
개발 중 실제로 겪은 예: 날짜 `<input>`에 `required` 속성을 넣었더니, 빈 값으로 제출할 때
브라우저 자체 검증 팝업("이 입력란을 작성하세요")이 먼저 뜨면서 우리가 작성한 JS의
커스텀 에러 메시지 분기가 전혀 실행되지 않는 문제가 있었다. 브라우저에서 실제로 클릭해보고
나서야 "코드는 있는데 도달하지 않는 분기"라는 걸 확인했고, 원인(HTML5 기본 검증이 `submit`
이벤트 자체를 막음)을 파악한 뒤 `required`를 제거해 커스텀 검증 로직이 실제로 실행되도록
고쳤다. — 이처럼 AI가 만든 코드도 "일단 실행해보고, 의도한 분기가 실제로 타는지"를 직접
확인해야 진짜 문제를 찾을 수 있다.
