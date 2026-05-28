# Golf Fit AI

골프 실력·미스샷·비거리·핸디캡 기반 클럽 추천 시스템 (MVP)

## 빠른 시작

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. MySQL DB 생성 (MySQL 콘솔에서)
CREATE DATABASE golf_fit_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에서 DB 비밀번호 수정

# 4. 초기 데이터 삽입
python seed_data.py

# 5. 서버 실행
uvicorn app.main:app --reload
```

## 확인 주소

| 주소 | 내용 |
|---|---|
| http://localhost:8000 | HTML 추천 폼 + 결과 화면 |
| http://localhost:8000/docs | Swagger UI |

## API 테스트 실행

서버 실행 + seed_data.py 완료 후:

```bash
python test_api.py
```

MySQL에 직접 연결해 17개 케이스를 검증합니다.

## 폴더 구조

```
golf_fit_ai/
├── app/
│   ├── db/database.py          # DB 연결 설정 (MySQL)
│   ├── models/                 # SQLAlchemy ORM 모델
│   ├── schemas/user_input.py   # Pydantic DTO
│   ├── services/
│   │   ├── recommendation.py   # 핵심 추천 로직
│   │   └── reason_builder.py   # 추천 이유 텍스트
│   ├── routers/recommend.py    # API 엔드포인트
│   └── main.py                 # 앱 진입점
├── static/css/style.css
├── static/js/app.js
├── templates/index.html
├── seed_data.py                # 초기 데이터 삽입
├── test_api.py                 # API 통합 테스트 (MySQL)
├── requirements.txt
└── .env.example
```

## 추후 확장 계획

- [ ] 온라인 최저가 조회
- [ ] scikit-learn 기반 추천 모델
- [ ] KoBERT 기반 추천 이유 생성
