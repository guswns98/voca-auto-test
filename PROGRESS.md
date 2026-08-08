# 똑똑보카 자동화 테스트 진행 상황

## 1. 목표

트리거스(주)의 **똑똑보카** 앱에 대한 E2E 자동화 테스트 구축.
- 프레임워크: **Python + Appium + pytest**
- 패턴: **POM (Page Object Model)**
- 리포트: **Allure Report**
- 대상 플랫폼: Android (Samsung R3CY70B5Z3B 단말 사용)
- **E2E 시나리오 방식**: 시나리오를 하나씩 추가하며 운영. 실패 시 스크린샷 + 로그로 원인 파악 후 수정.

---

## 2. 수행한 작업

### 2-1. 앱 분석 및 테스트 설계 (TEST_DESIGN.md)

- 웹 검색으로 똑똑보카 앱의 기능을 조사 (공식 사이트, Play Store, App Store, 기사 등)
- 총 34개 테스트 시나리오를 6개 영역(온보딩, 학습, 퀴즈, 보상, 습관, 설정)으로 설계
- P0/P1/P2 우선순위 분류

### 2-2. 프로젝트 초기 구조 생성

| 파일 | 설명 |
|------|------|
| `requirements.txt` | 의존성 (pytest, allure-pytest, Appium-Python-Client, selenium, python-dotenv) |
| `pytest.ini` | Allure 연동, 마커 정의 (p0/p1/p2, 기능별) |
| `config/settings.py` | Appium caps, 테스트 계정, 타임아웃 설정. `.env`에서 로드 |
| `.env.example` | 환경변수 템플릿 |
| `.gitignore` | venv, __pycache__, reports, .env 제외 |
| `conftest.py` | Appium 드라이버 session fixture + 앱 초기화 + 홈 화면 보장 |
| `run_tests.sh` | 마커별 테스트 실행 + Allure 리포트 생성 스크립트 |

### 2-3. POM 기본 클래스 (pages/base_page.py)

모든 Page Object의 부모 클래스. 제공 메서드:
- `find`, `find_clickable`, `find_all` — WebDriverWait 기반 요소 탐색
- `is_visible`, `is_present` — 요소 존재/가시성 확인 (타임아웃 지정 가능)
- `tap`, `type_text`, `get_text` — 기본 액션
- `swipe_up/down/left` — 스와이프
- `attach_screenshot` — Allure에 스크린샷 첨부
- `wait_for_text`, `tap_by_text` — 텍스트 기반 탐색 (Android/iOS 분기)

### 2-4. 화면 덤프 시스템

| 파일 | 설명 |
|------|------|
| `utils/screen_dumper.py` | 화면 fingerprint 생성 + 중복 감지 + XML/스크린샷/요소 저장 |
| `dump_screens.py` | 앱 화면 자동 순회 스크립트 |

### 2-5. 실제 단말 연결 및 앱 탐색

**비회원 가입 플로우 수동 진행 → 이후 카카오 로그인으로 전환:**
1. 앱 시작 → "가입 없이 시작하기" 탭
2. "이어서 이용하기" 탭 (비회원 경고 팝업)
3. "전체 동의합니다" → "확인" (약관 동의)
4. "영어" 선택 → "시작하기" (코스 선택)
5. "생활영어 기본" 선택 → "확인" (세부 코스)
6. "공부 코스 선택 완료!" → "시작하기"
7. 홈 화면 진입 완료

**이후 카카오 로그인으로 전환** (비회원 테스트는 보류)

### 2-6. 화면 덤프 결과

**앱 홈 화면 (회원 로그인 상태):**
- 상단: "영어" (현재 코스), 알림 아이콘, 캐시 잔액
- 퀴즈 카드: "지금 쌓인 퀴즈 3개!", "퀴즈 풀러 가기"
- 복권: "꽝없는 복권", "복권 긁기"
- 캐시 더 모으기: 학습미션, 추가 혜택 리스트
- 캐시 교환하기: 기프티콘, 현금 출금
- 학습하기: 보너스 퀴즈, 학습노트
- 하단: 학습통계, 설정

**잠금 화면 퀴즈 (앱 force-stop 후 재실행 시 뜸):**
- "레슨 1", "다음 단어의 뜻은?"
- 단어 + 4지선다 보기
- "밀어서 해제"
- "복권 긁기"
- 우측 하단 홈 버튼 (좌표: 959, 2029)

**코스 선택 화면:**
- "무엇을 공부하시겠어요?" 타이틀
- 7개 코스: 영어, 한자, 일본어, 국어 어휘, 성경, 중국어, 상식
- X 버튼: `content-desc='시트 닫기'`
- **물리 뒤로가기(driver.back()) 동작 안 함** → X 버튼으로만 닫기 가능
- X 누르면 "공부 코스 선택" 화면으로 이동 → 거기서 < 버튼으로 홈 복귀

### 2-7. conftest.py 주요 변경 이력

| 변경 | 이유 |
|------|------|
| `noReset` 기본값 `true`로 변경 | 앱이 매번 초기화되어 로그인 세션 날아감 |
| `activate_app` 제거 | Appium 세션이 caps로 앱 자동 실행하므로 중복 |
| `_dismiss_lock_screen()` 추가 | 앱 force-stop 후 재실행 시 잠금 화면 퀴즈가 먼저 뜸 |
| `_close_sheet()` 추가 | 코스 선택 등 시트 화면에서 driver.back() 안 먹힘 |
| `_ensure_home_screen()` 홈 폴링 강화 | 앱 로딩 시간 + Compose 렌더링 대기 |
| `ensure_home` fixture에 WebDriverException 처리 | UiAutomator2 크래시 시 앱 재시작 |
| `force-stop` 후 실행 | 기존 앱 프로세스 정리 후 깨끗한 상태에서 시작 |

### 2-8. E2E 시나리오 테스트 (현재 버전)

**운영 방식:** 시나리오를 하나씩 추가하며 실행. 실패 시 스크린샷 + 로그로 셀렉터 확인 후 수정.

현재 `tests/test_e2e_scenario.py`에 4개 시나리오:

| # | 시나리오 | 설명 |
|---|---------|------|
| E2E-01 | 앱 실행 후 홈 화면 확인 | 홈 또는 잠금 화면 퀴즈 표시 확인 |
| E2E-02 | 퀴즈 풀러가기 선택 | 퀴즈 진입 (셀렉터 미확정, 실패 스크린샷으로 확인 필요) |
| E2E-03 | 팝업창 X버튼 선택 | 시트 닫기 버튼으로 팝업 닫기 |
| E2E-04 | 홈 버튼 선택 | 우측 하단 홈 버튼 좌표 탭 → 앱 홈 화면 이동 |

### 2-9. 테스트 실행 결과 (지금까지)

| 실행 | E2E-01 | E2E-02 | E2E-03 | 이후 | 비고 |
|------|--------|--------|--------|------|------|
| 1차 | ✅ | ✅ | ✅ (코스) | ❌ 크래시 | UiAutomator2 크래시 연쇄 실패 |
| 2차 | ✅ | ✅ | ❌ | 연쇄 실패 | "영어" 탭 시 크래시 |
| 3차 | ✅ | ✅ | ❌ | 연쇄 실패 | 동일 |

**공통 실패 원인:** 특정 화면 진입 후 UiAutomator2 instrumentation 크래시 → 이후 모든 테스트 연쇄 실패

### 2-10. 기존 비회원 테스트 (보류)

`tests/` 하위에 비회원 기준 테스트 파일 3개 존재하나, 현재 사용하지 않음:

| 파일 | 테스트 수 | 상태 |
|------|----------|------|
| `tests/test_home.py` | 8개 | 보류 (회원 전환) |
| `tests/test_course.py` | 6개 | 보류 |
| `tests/test_notification.py` | 4개 | 보류 |

---

## 3. 현재 상태

- venv 생성 및 의존성 설치 **완료**
- Appium 서버 실행 중 (port 4723)
- 단말 연결됨 (R3CY70B5Z3B)
- **카카오 로그인 상태** (비회원 → 회원 전환 완료)
- E2E 시나리오 4개 작성 완료, **아직 실행 안 함**
- 이전 실행에서 UiAutomator2 크래시 발생 → Appium 재시작 필요할 수 있음

---

## 4. 남은 할 일

### 즉시
- [ ] E2E 시나리오 4개 실행
- [ ] 실패 시 Allure 스크린샷으로 셀렉터 확인 후 수정
- [ ] "퀴즈 풀러가기" 실제 셀렉터 확인 (이전 덤프에서 없었음)
- [ ] 팝업 X버튼 셀렉터 확인
- [ ] 통과 확인 후 다음 시나리오 추가

### 시나리오 추가 예정 (유저가 흐름 제공)
- 학습미션 진입
- 보너스 퀴즈 진입
- 기프티콘/현금 출금
- 학습노트/학습통계
- 설정
- 알림
- 복권

### 인프라
- [ ] Allure 리포트 생성 및 확인 (`allure serve reports/allure-results`)
- [ ] UiAutomator2 크래시 근본 원인 해결

---

## 5. 주의사항 및 결정 사항

### 앱 기술 스택
- **Jetpack Compose 기반** — `resource-id`가 거의 없어 `textContains` 셀렉터 위주로 사용
- clickable 요소가 `android.view.View` 타입이고 텍스트는 하위 `TextView`에 있음
- **Context는 NATIVE_APP만 존재** (WebView 없음)

### Appium 설정
- **appActivity**: `.inapp.MainActivity`
- **appPackage**: `com.knockknock.voca`
- **noReset: true** — 로그인 세션 유지 필수
- 세션 시작 전 `adb shell am force-stop` 실행하여 기존 프로세스 정리

### 화면 이동 주의사항
- **코스 선택 화면 등 시트 화면에서 `driver.back()` 동작 안 함** → `content-desc='시트 닫기'` X 버튼 사용 필수
- **코스 선택 X → "공부 코스 선택" 화면 → < 버튼(back) → 홈** (2단계 복귀)
- **앱 force-stop 후 재실행 시 잠금 화면 퀴즈가 먼저 뜸** → 우측 하단 홈 버튼(959, 2029) 탭으로 앱 홈 이동

### UiAutomator2 크래시 문제
- 특정 화면 진입 후 UiAutomator2 instrumentation이 크래시됨
- 크래시 발생 시 이후 모든 테스트가 연쇄 실패
- `ensure_home` fixture에서 WebDriverException 시 앱 재시작 처리 추가
- 근본 원인은 아직 미해결 (잠금 화면 오버레이와 충돌 가능성)

### 운영 방식
- **시나리오 하나씩 추가** — 유저가 흐름 제공 → 코드 작성 → 실행 → 실패 시 스크린샷으로 확인 → 수정
- **비회원 테스트 보류** — 카카오 로그인 회원 기준으로 진행
- **기존 app_automation 프로젝트와 별개** — 대상 앱, 구조, 인프라 모두 다름

### 셀렉터 전략
- Compose 앱이라 ID 기반 셀렉터 거의 불가
- `UiSelector().textContains(...)` 가 주요 전략
- `content-desc` (ACCESSIBILITY_ID) 사용 가능한 경우 활용 (예: "시트 닫기")
- 텍스트 없는 아이콘 버튼은 좌표 기반 탭 (예: 홈 버튼 959, 2029)
- clickable View는 인스턴스 인덱스로 구분 (`instance(0)`, `instance(1)`)

---

## 6. 파일 구조

```
triggers-auto/
├── config/
│   └── settings.py          # Appium caps, 환경설정
├── pages/
│   ├── __init__.py           # HomePage, CoursePage, NotificationPage export
│   ├── base_page.py          # POM 기본 클래스
│   ├── home_page.py          # 홈 화면 (실제 셀렉터)
│   ├── course_page.py        # 코스 선택 (실제 셀렉터)
│   ├── notification_page.py  # 알림 (실제 셀렉터)
│   ├── login_page.py         # 로그인 (추정 셀렉터, 미검증)
│   ├── onboarding_page.py    # 온보딩 (추정 셀렉터, 미검증)
│   ├── quiz_page.py          # 퀴즈 (추정 셀렉터, 미검증)
│   ├── cash_page.py          # 캐시 (추정 셀렉터, 미검증)
│   └── settings_page.py      # 설정 (추정 셀렉터, 미검증)
├── tests/
│   ├── test_e2e_scenario.py  # ★ E2E 시나리오 (현재 활성)
│   ├── test_home.py          # 비회원 홈 테스트 (보류)
│   ├── test_course.py        # 비회원 코스 테스트 (보류)
│   └── test_notification.py  # 비회원 알림 테스트 (보류)
├── utils/
│   └── screen_dumper.py      # 화면 덤프 유틸
├── dumps/                    # 화면 덤프 결과
├── reports/                  # Allure 리포트 결과
├── conftest.py               # pytest fixture (드라이버, 홈 보장, 스크린샷)
├── pytest.ini                # pytest 설정
├── requirements.txt          # 의존성
├── .env.example              # 환경변수 템플릿
├── .gitignore
├── dump_screens.py           # 화면 순회 스크립트
├── run_tests.sh              # 테스트 실행 스크립트
├── TEST_DESIGN.md            # 테스트 설계 문서
└── PROGRESS.md               # 이 파일
```
