#!/bin/bash
# 똑똑보카 자동화 테스트 실행 스크립트

set -e

REPORT_DIR="reports/allure-results"
REPORT_HTML="reports/allure-report"

# 사용법 출력
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all           모든 테스트 실행"
    echo "  --p0            P0 (핵심) 테스트만 실행"
    echo "  --p1            P1 (주요) 테스트만 실행"
    echo "  --auth          인증 테스트만 실행"
    echo "  --learn         학습 테스트만 실행"
    echo "  --quiz          퀴즈 테스트만 실행"
    echo "  --cash          보상 테스트만 실행"
    echo "  --setting       설정 테스트만 실행"
    echo "  --report        Allure 리포트 생성 및 열기"
    echo "  --help          도움말"
    echo ""
    echo "Examples:"
    echo "  $0 --p0                    # P0 테스트만 실행"
    echo "  $0 --auth --quiz           # 인증 + 퀴즈 테스트 실행"
    echo "  $0 --all --report          # 전체 실행 후 리포트 열기"
}

# 테스트 실행
run_tests() {
    local markers="$1"
    if [ -n "$markers" ]; then
        python -m pytest -m "$markers" --alluredir="$REPORT_DIR" -v
    else
        python -m pytest --alluredir="$REPORT_DIR" -v
    fi
}

# Allure 리포트 생성
generate_report() {
    if command -v allure &> /dev/null; then
        allure generate "$REPORT_DIR" -o "$REPORT_HTML" --clean
        allure open "$REPORT_HTML"
    else
        echo "Allure CLI가 설치되어 있지 않습니다."
        echo "설치: brew install allure (macOS)"
        echo "결과 파일 위치: $REPORT_DIR"
    fi
}

# 인자 파싱
MARKERS=""
OPEN_REPORT=false

if [ $# -eq 0 ]; then
    usage
    exit 0
fi

for arg in "$@"; do
    case $arg in
        --all)
            MARKERS=""
            ;;
        --p0)
            MARKERS="${MARKERS:+$MARKERS or }p0"
            ;;
        --p1)
            MARKERS="${MARKERS:+$MARKERS or }p1"
            ;;
        --auth)
            MARKERS="${MARKERS:+$MARKERS or }auth"
            ;;
        --learn)
            MARKERS="${MARKERS:+$MARKERS or }learn"
            ;;
        --quiz)
            MARKERS="${MARKERS:+$MARKERS or }quiz"
            ;;
        --cash)
            MARKERS="${MARKERS:+$MARKERS or }cash"
            ;;
        --setting)
            MARKERS="${MARKERS:+$MARKERS or }setting"
            ;;
        --report)
            OPEN_REPORT=true
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $arg"
            usage
            exit 1
            ;;
    esac
done

# 실행
if [ "$OPEN_REPORT" = true ] && [ -z "$MARKERS" ] && [ $# -eq 1 ]; then
    # --report만 입력한 경우 리포트만 열기
    generate_report
else
    run_tests "$MARKERS"
    if [ "$OPEN_REPORT" = true ]; then
        generate_report
    fi
fi
