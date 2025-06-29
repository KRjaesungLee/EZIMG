# DALL-E 이미지 생성기

Vue.js 프론트엔드와 FastAPI 백엔드를 사용한 DALL-E 이미지 생성 애플리케이션입니다.

## 기능

- 텍스트 프롬프트를 입력하여 DALL-E로 이미지 생성
- 생성된 이미지 다운로드
- 실시간 로딩 상태 표시
- 에러 처리

## 설치 및 실행

### 백엔드 설정

1. 백엔드 디렉토리로 이동:

```bash
cd backend
```

2. 가상환경 활성화:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:

   - `backend` 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   - OpenAI API 키는 [OpenAI 웹사이트](https://platform.openai.com/api-keys)에서 발급받을 수 있습니다.

5. 백엔드 서버 실행:

```bash
python main.py
```

백엔드 서버는 `http://localhost:8000`에서 실행됩니다.

### 프론트엔드 설정

1. 프론트엔드 디렉토리로 이동:

```bash
cd frontend
```

2. 필요한 패키지 설치:

```bash
npm install
```

3. 개발 서버 실행:

```bash
npm run dev
```

프론트엔드는 `http://localhost:5173`에서 실행됩니다.

## 사용법

1. 브라우저에서 `http://localhost:5173`에 접속
2. 텍스트 영역에 생성하고 싶은 이미지를 설명
3. "이미지 생성" 버튼 클릭
4. 생성된 이미지 확인 및 다운로드

## 기술 스택

### 프론트엔드

- Vue.js 3
- TypeScript
- Axios
- Vite

### 백엔드

- FastAPI
- OpenAI API
- Python 3.11

## API 엔드포인트

- `GET /`: API 상태 확인
- `POST /generate-image`: DALL-E 이미지 생성
  - Request Body: `{"prompt": "이미지 설명"}`
  - Response: `{"image_url": "생성된 이미지 URL"}`
