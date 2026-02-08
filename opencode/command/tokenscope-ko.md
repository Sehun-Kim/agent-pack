---
description: 토큰 사용량을 핵심 숫자만 한국어 표로 요약
---

아래 순서대로 실행해.

1) tokenscope 툴을 직접 호출한다. (다른 에이전트에게 delegate 금지)
2) /Users/a14818/agent-pack/token-usage-output.txt 를 읽는다.
3) 읽은 내용에서 **핵심 숫자만** 뽑아서 **한국어 표(마크다운 테이블)만** 출력한다.

출력 규칙:
- 표 외의 텍스트(설명/해석/추가 문장/코드블록) 금지
- 표는 아래 항목을 **가능한 한 모두** 포함
  - 세션 ID ("Token Analysis: Session ...")
  - 모델 ("Model: ...")
  - 입력 토큰(신규) ("Input tokens:")
  - 캐시 읽기 ("Cache read:")
  - 캐시 쓰기 ("Cache write:")
  - 출력 토큰 ("Output tokens:")
  - 세션 총 토큰(청구) ("Session Total:")
  - 실제 비용 ("ACTUAL COST (from API):")
  - API 호출 수 ("All N API calls"에서 N)
- 값이 없거나 못 찾으면 해당 행의 값은 "N/A"로 표기
- 만약 출력에 "[Project README:" 같은 블록이 섞여 나오면 **그 이후는 전부 무시**하고 표에 포함하지 않는다.

표 형식(예시):
| 항목 | 값 |
|---|---|
| 세션 ID | ... |
