# Golf Fit AI

골퍼의 핸디캡, 비거리, 미스샷 유형, 탄도 성향 등을 분석하여 적합한 골프 클럽 카테고리와 실제 클럽 모델을 추천하는 AI 기반 추천 시스템이다.

FastAPI, MySQL, SQLAlchemy 기반으로 구현하였으며, Rule-Based 추천 엔진과 Machine Learning(RandomForest) 모델을 함께 활용한다.

---

# 주요 기능

### 1. 클럽 종류별 추천

사용자는 아래 클럽 중 원하는 추천 대상을 선택할 수 있다.

* Driver
* Wood
* Utility
* Iron
* Wedge
* Putter

선택한 클럽 종류 외의 카테고리는 추천되지 않는다.

---

### 2. Rule-Based 추천 엔진

입력값:

* Handicap
* 비거리
* 미스샷 유형
* 탄도
* 스윙 속도

를 기반으로 규칙 엔진이 추천 점수를 계산한다.

출력:

* 추천 카테고리 Top3
* 추천 점수(score)
* 추천 이유(reason)
* 추천 근거(matched_traits)

---

### 3. 실제 클럽 모델 추천

추천된 카테고리에 속하는 실제 클럽 모델을 함께 추천한다.

예시:

* Ping G430 MAX
* TaylorMade Qi10
* Callaway Paradym

출력 정보:

* 브랜드
* 모델명
* 로프트
* 샤프트
* 플렉스
* 가격대
* 구매 링크

---

### 4. Machine Learning 추천

Rule-Based 추천 결과를 이용하여 학습 데이터를 생성하고 RandomForestClassifier를 학습하였다.

ML 모델은:

* 추천 카테고리 예측
* 예측 신뢰도(confidence) 계산
* Rule-Based 결과와 비교

기능을 수행한다.

응답 예시:

```json
{
  "rule_top1": "슬라이스 보정 드라이버",
  "ml_prediction": {
    "category_name": "슬라이스 보정 드라이버",
    "confidence": 0.31
  },
  "ml_agreement": true
}
```

---

# 시스템 구조

```text
사용자 입력
        │
        ▼
Rule-Based 추천 엔진
        │
        ├── 추천 카테고리 Top3
        │
        ├── 추천 이유 생성
        │
        └── 실제 클럽 모델 조회
                    │
                    ▼
               MySQL DB

동시에

사용자 입력
        │
        ▼
RandomForest Model
        │
        ▼
ML Prediction
```

---

# 기술 스택

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic

### Database

* MySQL

### Machine Learning

* scikit-learn
* RandomForestClassifier

### Frontend

* HTML
* CSS
* JavaScript

---

# 빠른 시작

```bash
pip install -r requirements.txt
```

MySQL DB 생성

```sql
CREATE DATABASE golf_fit_ai
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

환경 변수 설정

```bash
cp .env.example .env
```

초기 데이터 삽입

```bash
python seed_data.py
```

서버 실행

```bash
python -m uvicorn app.main:app --reload
```

---

# API 테스트

```bash
python test_api.py
```

검증 항목:

* Driver 추천
* Wood 추천
* Utility 추천
* Iron 추천
* Wedge 추천
* Putter 추천
* Validation 테스트

총 14개 테스트 케이스를 검증한다.

---

# ML 학습 파이프라인

학습 데이터 생성

```bash
python scripts/generate_training_data.py
```

모델 학습

```bash
python scripts/train_model.py
```

생성 파일:

```text
data/training_data.csv
models/recommendation_model.joblib
```

---

# 프로젝트 구조

```text
golf_fit_ai/
├── app/
├── scripts/
├── static/
├── templates/
├── data/
├── models/
├── seed_data.py
├── test_api.py
├── requirements.txt
└── README.md
```

---

# 향후 개선 계획

* 실시간 최저가 조회
* 온라인 쇼핑몰 연동
* 사용자 플레이 기록 저장
* 실제 사용자 데이터 기반 재학습
* XGBoost / LightGBM 모델 비교
* 추천 정확도 평가 대시보드
