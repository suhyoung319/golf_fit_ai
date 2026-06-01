# Golf Fit AI

골퍼의 핸디캡, 비거리, 미스샷 유형, 탄도 성향을 바탕으로 적합한 골프 클럽 카테고리와 실제 클럽 모델을 추천하는 FastAPI 기반 추천 시스템입니다.

Rule-Based 추천 엔진을 중심으로 Top3 추천 결과를 제공하고, 학습된 RandomForest 모델이 있을 경우 ML 예측 결과와 Rule-Based 1위 추천의 일치 여부를 함께 보여줍니다. 화면에서는 `ML 기반 예측 결과` 카드와 `Rule 기반 추천 Top3` 영역을 분리해 표시합니다. 추천된 실제 클럽에는 `club_prices` 테이블 기반의 샘플 판매처 가격 비교 기능도 제공합니다.

---

## 주요 기능

### 1. 클럽 종류별 Top3 추천

사용자는 아래 클럽 종류 중 하나를 선택해 추천을 받을 수 있습니다.

- Driver
- Wood
- Utility
- Iron
- Wedge
- Putter

선택한 클럽 종류에 해당하는 카테고리 안에서만 추천이 이루어지며, 추천 결과는 점수 기준 Top3로 반환됩니다. 웹 화면에서는 이 목록을 `Rule 기반 추천 Top3`로 표시합니다.

### 2. Rule-Based 추천 엔진

입력값을 기반으로 클럽 카테고리별 점수를 계산합니다.

- Handicap
- 비거리
- 미스샷 유형
- 탄도
- 스윙 속도
- 퍼팅/웨지/유틸리티별 세부 입력값

응답에는 추천 카테고리, 추천 점수, 추천 이유, 점수 산출 근거가 포함됩니다.

### 3. 실제 클럽 모델 추천

추천된 카테고리에 속하는 실제 클럽 모델을 함께 제공합니다.

포함 정보:

- 브랜드
- 모델명
- 로프트
- 샤프트
- 플렉스
- 가격대
- 구매 검색 링크
- 관용성/거리/컨트롤/스핀 점수

### 4. 클럽 가격 비교

추천 클럽 카드에서 `최저가 보기` 버튼을 누르면 해당 클럽의 판매처 가격 목록을 확인할 수 있습니다.

이 기능은 실시간 크롤링이 아니라 `club_prices` 테이블에 저장된 샘플 가격 데이터를 기반으로 합니다.

- 판매처명
- 상품명
- 가격
- 구매 링크
- 가격 오름차순 정렬
- 가장 저렴한 항목에 `최저가` 표시

### 5. Machine Learning 보조 예측

Rule-Based 추천 결과로 생성한 학습 데이터를 이용해 RandomForestClassifier를 학습할 수 있습니다.

ML 모델은 Rule-Based 추천을 대체하지 않고, 보조 예측 정보로만 사용됩니다.

웹 화면에서는 추천 결과 상단에 `ML 기반 예측 결과` 카드가 표시됩니다.

- 예측 카테고리: `ml_prediction.category_name`
- 예측 신뢰도: `ml_prediction.confidence * 100`을 소수점 1자리 퍼센트로 표시
- Rule 1순위와 ML 예측이 같으면 `Rule 1순위와 일치`
- 다르면 `Rule 1순위와 불일치`
- ML 모델을 불러오지 못하면 Rule 기반 추천만 표시한다는 안내 문구 표시

응답 예시:

```json
{
  "club_type": "driver",
  "handicap": 28,
  "calculated_skill": "beginner",
  "rule_top1": "슬라이스 보정 드라이버",
  "ml_prediction": {
    "category_name": "슬라이스 보정 드라이버",
    "confidence": 0.31
  },
  "ml_agreement": true,
  "recommendations": []
}
```

모델 파일이 없거나 예측에 실패해도 API는 정상 동작하며, 이 경우 `ml_prediction`과 `ml_agreement`는 `null`이 될 수 있습니다.

예를 들어 `confidence`가 `0.235`라면 화면에는 `23.5%`로 표시됩니다.

---

## 시스템 흐름

```text
사용자 입력
   │
   ▼
Pydantic 입력 검증
   │
   ▼
Rule-Based 추천 엔진
   │
   ├─ 카테고리별 점수 계산
   ├─ 추천 카테고리 Top3 선정
   ├─ 추천 이유 생성
   └─ 실제 클럽 모델 조회
        │
        ▼
      MySQL DB
        │
        ├─ clubs
        ├─ club_categories
        └─ club_prices

동시에, 모델 파일이 있으면:

사용자 입력
   │
   ▼
RandomForest Model
   │
   ▼
ML 예측 + Rule 1위 일치 여부
   │
   ▼
화면 상단 ML 예측 카드
```

---

## 기술 스택

Backend:

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- PyMySQL

Database:

- MySQL

Machine Learning:

- scikit-learn
- pandas
- joblib
- RandomForestClassifier

Frontend:

- HTML
- CSS
- JavaScript

---

## 빠른 시작

패키지 설치:

```bash
pip install -r requirements.txt
```

MySQL DB 생성:

```sql
CREATE DATABASE golf_fit_ai
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

환경 변수 설정:

```bash
cp .env.example .env
```

`.env`에서 DB 접속 정보를 자신의 환경에 맞게 수정합니다.

초기 데이터 삽입:

```bash
python seed_data.py
```

현재 시드 데이터는 아래 샘플 데이터를 생성합니다.

- 19개 클럽 카테고리
- 57개 실제 클럽 모델
- 171개 판매처 가격 데이터

서버 실행:

```bash
python -m uvicorn app.main:app --reload
```

접속:

- 웹 화면: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

---

## API

### 추천 API

```text
POST /api/recommend/driver
POST /api/recommend/wood
POST /api/recommend/utility
POST /api/recommend/iron
POST /api/recommend/wedge
POST /api/recommend/putter
```

각 API는 클럽 종류별 입력값을 받아 Rule-Based Top3 추천과 ML 보조 예측 결과를 반환합니다.

주요 응답 필드:

- `rule_top1`: Rule 기반 추천 1순위 카테고리
- `ml_prediction.category_name`: ML 모델이 예측한 카테고리
- `ml_prediction.confidence`: ML 예측 신뢰도
- `ml_agreement`: Rule 1순위와 ML 예측의 일치 여부
- `recommendations`: Rule 기반 추천 Top3 목록

### 클럽 가격 API

```text
GET /api/clubs/{club_id}/prices
```

특정 클럽의 판매처 가격 목록을 조회합니다.

특징:

- `price` 오름차순 정렬
- 가장 저렴한 항목이 첫 번째로 반환
- 존재하지 않는 `club_id`는 404 반환

응답 예시:

```json
[
  {
    "id": 1,
    "club_id": 1,
    "seller_name": "골프존마켓",
    "product_name": "TaylorMade Stealth 2 HD 공식 정품",
    "price": 480000,
    "product_url": "https://www.google.com/search?q=..."
  }
]
```

---

## 테스트

```bash
python test_api.py
```

검증 항목:

- Driver 추천
- Wood 추천
- Utility 추천
- Iron 추천
- Wedge 추천
- Putter 추천
- 입력값 Validation 실패 케이스
- Rule Top1과 ML 예측 일치 여부 필드 검증
- ML 모델 파일이 없을 때도 API가 실패하지 않는지 검증
- 클럽 가격 목록 조회
- 존재하지 않는 클럽 가격 API 404 검증

현재 테스트 결과:

```text
16/16 통과
```

---

## ML 학습 파이프라인

학습 데이터 생성:

```bash
python scripts/generate_training_data.py
```

모델 학습:

```bash
python scripts/train_model.py
```

생성 파일:

```text
data/training_data.csv
models/recommendation_model.joblib
```

`data/training_data.csv`와 `models/recommendation_model.joblib`은 재생성 가능한 산출물이므로 Git 추적 대상에서 제외됩니다.

---

## 프로젝트 구조

```text
golf_fit_ai/
├── app/
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   ├── club.py
│   │   ├── club_price.py
│   │   ├── recommendation.py
│   │   ├── user.py
│   │   └── user_golf_profile.py
│   ├── routers/
│   │   └── recommend.py
│   ├── schemas/
│   │   └── user_input.py
│   ├── services/
│   │   ├── ml_recommendation.py
│   │   ├── reason_builder.py
│   │   ├── recommendation.py
│   │   └── scorer.py
│   └── main.py
├── scripts/
│   ├── generate_training_data.py
│   └── train_model.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   └── index.html
├── data/
│   └── training_data.csv
├── models/
│   └── recommendation_model.joblib
├── .env.example
├── seed_data.py
├── test_api.py
├── requirements.txt
└── README.md
```

---

## 향후 개선 계획

- 실시간 최저가 크롤링 또는 외부 쇼핑몰 API 연동
- 실제 구매처 API 기반 가격 갱신 스케줄러
- 사용자 플레이 기록 저장
- 추천 이력 기반 개인화
- 실제 사용자 데이터 기반 재학습
- XGBoost / LightGBM 모델 비교
- 추천 정확도 평가 대시보드
