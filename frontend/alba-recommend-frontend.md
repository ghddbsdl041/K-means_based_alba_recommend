# 사용자 맞춤형 알바 추천 서비스 — 프론트엔드 개발 명세

> Claude Code 기반 개발용 명세서  
> 작성 기준: 2025년 6월

---

## 1. 프로젝트 개요

### 서비스 소개
기존의 조건 필터 기반 알바 탐색 방식에서 벗어나, 사용자가 자신의 근무 성향을 명확히 알지 못하는 상태에서도 최적의 아르바이트를 추천받을 수 있는 **성향 기반 매칭 시스템**.

사용자 인터랙티브 설문 → 성향 벡터 도출 → K-Means 군집 매칭 → 맞춤 공고 추천

### 타깃 유저
서울 거주 20대 청년층, 특히 알바 경험이 적은 대학생

### 서비스 성격
직접 채용 없음. 공고 원문 URL을 통해 알바몬·알바천국으로 이동하는 **중개형 서비스**

---

## 2. 기술 스택

| 영역 | 스택 |
|------|------|
| 프레임워크 | Next.js 15 (App Router) |
| 언어 | TypeScript |
| 스타일링 | Tailwind CSS v4 |
| 상태관리 | React useState / useReducer (로컬) |
| HTTP | fetch API (백엔드 FastAPI 연동) |
| 배포 | Vercel |

---

## 3. 디자인 시스템

### 디자인 콘셉트
"투명하고 깔끔한 Glassmorphism"

- 배경: 연보라~흰색 그라데이션 (`#F5F3FF` → `#FFFFFF`)
- 카드: `backdrop-blur` + 반투명 흰색 배경 (`bg-white/60`)
- 테두리: `rounded-2xl`, `border border-white/40`
- 그림자: `shadow-sm` (과하지 않게)
- 색상 포인트: 바이올렛 계열 (`#7C3AED`, `#A78BFA`)

### 컬러 팔레트

```css
--color-bg-start: #F0EDFF;
--color-bg-end: #FFFFFF;
--color-primary: #7C3AED;       /* 주요 액션, 선택 강조 */
--color-primary-light: #A78BFA; /* 진행바, 보조 */
--color-primary-soft: #EDE9FE;  /* 선택된 카드 배경 */
--color-text-main: #1C1B2E;
--color-text-sub: #6B7280;
--color-border: rgba(255,255,255,0.4);
--color-card-bg: rgba(255,255,255,0.6);
```

### 타이포그래피

| 역할 | 폰트 | 굵기 |
|------|------|------|
| Display (히어로 타이틀) | Pretendard | 700–800 |
| 질문 텍스트 | Pretendard | 600 |
| 본문·공고 정보 | Pretendard | 400–500 |
| 영문 보조 | Inter | 500 |

```html
<!-- _app or layout.tsx에 추가 -->
<link rel="preconnect" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css" />
```

---

## 4. 페이지 구성 및 라우팅

```
/                   → 랜딩 페이지 (LandingPage)
/survey             → 성향 설문 페이지 (SurveyPage)
/result             → 성향 결과 + 추천 공고 리스트 (ResultPage)
```

---

## 5. 페이지별 상세 명세

---

### 5-1. 랜딩 페이지 (`/`)

#### 목적
"이 서비스가 무엇인지" 즉각적으로 인지시키기. 불필요한 UI 없이 핵심만.

#### 레이아웃 구성

```
┌──────────────────────────────────────┐
│  (배경: 연보라 그라데이션)             │
│                                      │
│   [서비스 로고/이름]                  │
│                                      │
│   나에게 맞는 알바,                   │
│   조건 말고 성향으로 찾아요.           │
│   (서브 카피 1줄)                     │
│                                      │
│   [ 내 성향 알바 찾기 →  ]  ← CTA    │
│                                      │
│   ─────────────────────────────────  │
│   특징 3가지 (아이콘 + 짧은 텍스트)   │
└──────────────────────────────────────┘
```

#### 카피 (참고)
- 히어로 타이틀: `나에게 맞는 알바,\n성향으로 찾아요.`
- 서브: `조건 필터 말고, 5가지 질문으로 딱 맞는 알바를 추천받아 보세요.`
- CTA 버튼: `지금 시작하기 →`

#### 특징 3가지 아이템 (아이콘 + 텍스트)
1. `✦ 5문항 성향 설문` — 간단한 선택으로 내 근무 스타일 파악
2. `✦ AI 기반 매칭` — K-Means 클러스터링으로 최적 공고 추천
3. `✦ 실시간 공고 연결` — 알바몬·알바천국 최신 공고 바로 연결

#### 컴포넌트
- `<HeroSection />` — 타이틀 + CTA
- `<FeatureStrip />` — 3가지 특징 (가로 배열 또는 세로)

---

### 5-2. 설문 페이지 (`/survey`)

#### 목적
밸런스 게임·MBTI처럼 **흥미 유발**, 질문에 집중, 가독성 우수

#### 설문 로직 (조건부 표시)

```
Q1 (필수) → 무조건 표시
  └─ Q1 = B → Q2 표시 (필수)
                └─ Q2 = B → Q3 표시 (필수)
Q4 (필수) → 무조건 표시
Q5 (필수) → 무조건 표시
```

**Q2, Q3는 조건부이며, 해당 조건 미충족 시 API 요청에서 해당 파라미터 제외**

#### 질문 데이터 정의

```typescript
// types/survey.ts
export type AnswerValue = "A" | "B";

export interface Question {
  id: "Q1" | "Q2" | "Q3" | "Q4" | "Q5";
  text: string;
  optionA: { label: string; description: string };
  optionB: { label: string; description: string };
  condition?: { questionId: string; requiredValue: AnswerValue };
  required: boolean;
}

export const QUESTIONS: Question[] = [
  {
    id: "Q1",
    text: "선호하는 근무 형태 혹은 목적이 무엇인가요?",
    optionA: { label: "급전 / 단기", description: "단기 고수익형" },
    optionB: { label: "꾸준히 / 안정성", description: "장기 안정형" },
    required: true,
  },
  {
    id: "Q2",
    text: "어떤 근무 환경 및 직무를 선호하시나요?",
    optionA: { label: "실내 / 사무", description: "차분한 내근 업무" },
    optionB: { label: "현장 / 서비스", description: "활동적인 대면 업무" },
    condition: { questionId: "Q1", requiredValue: "B" },
    required: true,
  },
  {
    id: "Q3",
    text: "원하시는 근무 시간 및 고용 형태는 무엇인가요?",
    optionA: { label: "가벼운 파트타임", description: "짧은 시간의 파트타임" },
    optionB: { label: "풀타임 정규직급", description: "고정적인 매장관리 및 풀타임" },
    condition: { questionId: "Q2", requiredValue: "B" },
    required: true,
  },
  {
    id: "Q4",
    text: "선호하는 하루 중 근무 시간대는 언제인가요?",
    optionA: { label: "주간 선호", description: "아침~오후 근무 선호" },
    optionB: { label: "야간 선호", description: "저녁~심야 근무 선호" },
    required: true,
  },
  {
    id: "Q5",
    text: "선호하는 근무 요일 패턴은 무엇인가요?",
    optionA: { label: "평일 위주", description: "월~금 근무 선호" },
    optionB: { label: "주말 위주", description: "토/일 주말 근무 선호" },
    required: true,
  },
];
```

#### UI 레이아웃

```
┌─────────────────────────────────────────┐
│  ← 뒤로   [●●●○○] 3/5                  │  ← 상단 진행 표시 (프로그레스바)
│                                         │
│                                         │
│   Q3. 원하시는 근무 시간 및              │
│       고용 형태는 무엇인가요?            │  ← 질문 텍스트 (크고 굵게)
│                                         │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │                 │  │               │ │
│  │  A              │  │  B            │ │  ← 선택 카드 2개 (가로 배열)
│  │  가벼운         │  │  풀타임       │ │     호버 시 보라색 테두리
│  │  파트타임       │  │  정규직급     │ │     선택 시 배경색 변경
│  │                 │  │               │ │
│  │  짧은 시간의    │  │  고정적인     │ │
│  │  파트타임       │  │  매장관리 및  │ │
│  │                 │  │  풀타임       │ │
│  └─────────────────┘  └───────────────┘ │
│                                         │
│         [ 다음 →  ]                     │  ← 선택 후 활성화
└─────────────────────────────────────────┘
```

#### 선택 카드 스타일 (Tailwind 예시)

```tsx
// 기본 상태
className="rounded-2xl border border-gray-200 bg-white/60 backdrop-blur-sm p-6 cursor-pointer
           transition-all duration-200 hover:border-violet-400 hover:shadow-md"

// 선택된 상태
className="rounded-2xl border-2 border-violet-500 bg-violet-50/80 backdrop-blur-sm p-6 cursor-pointer
           shadow-md shadow-violet-100"
```

#### 진행 상태 관리

```typescript
// hooks/useSurvey.ts
interface SurveyState {
  answers: Partial<Record<"Q1"|"Q2"|"Q3"|"Q4"|"Q5", AnswerValue>>;
  currentStep: number;         // 현재 표시 중인 질문 인덱스
  visibleQuestions: Question[]; // 조건부 로직 반영 후 표시할 질문 배열
}
```

#### 설문 완료 후 처리
- 모든 필수 질문 답변 완료 시 `/result` 페이지로 이동
- 답변 데이터는 `sessionStorage` 또는 URL query params로 전달

---

### 5-3. 결과 페이지 (`/result`)

#### 구성
1. **성향 분석 결과 카드** (상단)
2. **추천 알바 공고 리스트** (하단)

---

#### 5-3-1. 성향 분석 결과 카드

레퍼런스: BAND 앱의 유저 DNA 결과 카드 (이미지 2, 3 참고)

```
┌──────────────────────────────────────────┐
│                                          │
│   당신의 알바 성향은                      │
│                                          │
│   ┌──────────────────────────────────┐   │
│   │  [캐릭터 이미지 영역 - 추후 삽입] │   │  ← 160×160px 비워두기 (추후 LLM 생성 이미지)
│   │  (placeholder: 둥근 회색 박스)   │   │
│   └──────────────────────────────────┘   │
│                                          │
│       {cluster_name}                     │  ← API 응답값 (크고 굵게, 보라색)
│                                          │  cluster_id 0 → "일반 파트타임 서비스형"
│                                          │  cluster_id 1 → "정규 식음료/매장관리형"
│                                          │  cluster_id 2 → "안정적 사무/CS형"
│                                          │  cluster_id 3 → "고수익 단기/노무형"
│       {CLUSTER_TRAITS[cluster_id].description} │  ← 유형 설명 (작은 서브텍스트)
│                                          │
│   에너지력  ████████░░  {value}%         │
│   유연성    ██████░░░░  {value}%         │
│   집중력    ████░░░░░░  {value}%         │
│   사교성    ██████████  {value}%         │  ← 성향 지표 바 (cluster_id 기반)
│                                          │
└──────────────────────────────────────────┘
```

**캐릭터 이미지 플레이스홀더:**
```tsx
<div className="w-40 h-40 rounded-full bg-gray-100 border-2 border-dashed border-gray-300
                flex items-center justify-center text-gray-400 text-sm mx-auto">
  캐릭터 준비 중
</div>
```

**성향 지표 값 (cluster_id 기반 고정값 매핑):**

```typescript
// constants/clusterTraits.ts
export const CLUSTER_TRAITS: Record<number, {
  description: string;
  traits: { label: string; value: number }[];  // value: 0~100
}> = {
  0: {
    description: "유연하게, 내 페이스로 시작하는 스타일",
    traits: [
      { label: "에너지력", value: 40 },
      { label: "유연성",   value: 90 },
      { label: "집중력",   value: 50 },
      { label: "사교성",   value: 60 },
    ],
  },
  1: {
    description: "든든한 보장 속에서 전문성을 쌓는 스타일",
    traits: [
      { label: "에너지력", value: 70 },
      { label: "유연성",   value: 40 },
      { label: "집중력",   value: 75 },
      { label: "사교성",   value: 80 },
    ],
  },
  2: {
    description: "조용한 실내에서 집중하며 안정을 추구하는 스타일",
    traits: [
      { label: "에너지력", value: 30 },
      { label: "유연성",   value: 30 },
      { label: "집중력",   value: 90 },
      { label: "사교성",   value: 70 },
    ],
  },
  3: {
    description: "빠르게 벌고 자유롭게 쉬는 스타일",
    traits: [
      { label: "에너지력", value: 95 },
      { label: "유연성",   value: 80 },
      { label: "집중력",   value: 40 },
      { label: "사교성",   value: 30 },
    ],
  },
};
```

---

#### 5-3-2. 추천 알바 공고 리스트

**레이아웃: 1열 N행, 가로로 긴 카드**

```
┌─────────────────────────────────────────────────────────────────┐
│  {company_name}                              {cluster_name}      │
│                                                                  │
│  {title}                                                         │
│                                                                  │
│  💰 {pay_info}   ⏰ {work_time}   📍 {region}                    │
│                                                                  │
│  # {category 태그들}                                              │
│                                                         [공고 보기→] │
└─────────────────────────────────────────────────────────────────┘
```

**카드 컴포넌트 (`JobCard.tsx`):**

```tsx
interface Job {
  cluster_id: number;
  cluster_name: string;
  company_name: string;
  title: string;
  pay_info: string;
  work_time: string;
  region: string;
  detail_url: string;
  category: string;
}
```

**카드 스타일:**
```tsx
className="w-full rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm
           p-5 hover:shadow-md hover:border-violet-200 transition-all duration-200"
```

**"공고 보기" 버튼:**
```tsx
<a
  href={job.detail_url}
  target="_blank"
  rel="noopener noreferrer"
  className="ml-auto shrink-0 px-4 py-2 rounded-xl bg-violet-600 text-white text-sm
             font-medium hover:bg-violet-700 transition-colors"
>
  공고 보기 →
</a>
```

---

## 6. API 연동 명세

### 엔드포인트

```
POST https://alba-backend-1037394136554.us-central1.run.app/api/recommend
```

### Request Body

```typescript
interface RecommendRequest {
  q1_answer: "A" | "B";
  q2_answer?: "A" | "B";   // Q1=B일 때만 포함
  q3_answer?: "A" | "B";   // Q2=B일 때만 포함
  q4_answer: "A" | "B";
  q5_answer: "A" | "B";
  limit: number;            // 100 고정
}
```

### Response Body

```typescript
interface Job {
  cluster_id: number;
  cluster_name: string;
  company_name: string;
  title: string;
  pay_info: string;
  work_time: string;
  region: string;
  detail_url: string;       // 알바몬 또는 알바천국 공고 URL
  category: string;         // 쉼표 구분 문자열
}

type RecommendResponse = Job[];
```

### API 호출 함수

```typescript
// lib/api.ts
export async function fetchRecommendations(answers: SurveyAnswers): Promise<Job[]> {
  const body: RecommendRequest = {
    q1_answer: answers.Q1,
    q4_answer: answers.Q4,
    q5_answer: answers.Q5,
    limit: 100,
  };

  // 조건부 파라미터
  if (answers.Q1 === "B" && answers.Q2) body.q2_answer = answers.Q2;
  if (answers.Q2 === "B" && answers.Q3) body.q3_answer = answers.Q3;

  const res = await fetch(
    "https://alba-backend-1037394136554.us-central1.run.app/api/recommend",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }
  );

  if (!res.ok) throw new Error("추천 공고를 불러오지 못했습니다.");
  return res.json();
}
```

---

## 7. 폴더 구조

```
src/
├── app/
│   ├── page.tsx              # 랜딩 페이지
│   ├── survey/
│   │   └── page.tsx          # 설문 페이지
│   ├── result/
│   │   └── page.tsx          # 결과 + 공고 리스트 페이지
│   └── layout.tsx
├── components/
│   ├── landing/
│   │   ├── HeroSection.tsx
│   │   └── FeatureStrip.tsx
│   ├── survey/
│   │   ├── QuestionCard.tsx  # 선택 카드 2개
│   │   ├── ProgressBar.tsx
│   │   └── SurveyLayout.tsx
│   ├── result/
│   │   ├── PersonaCard.tsx   # 성향 분석 결과 카드
│   │   ├── TraitBar.tsx      # 성향 지표 바
│   │   ├── JobList.tsx       # 공고 리스트
│   │   └── JobCard.tsx       # 개별 공고 카드
│   └── ui/
│       └── Button.tsx
├── constants/
│   └── clusterTraits.ts      # cluster_id별 성향 지표
├── hooks/
│   └── useSurvey.ts          # 설문 상태 관리 훅
├── lib/
│   └── api.ts                # API 호출 함수
└── types/
    ├── survey.ts
    └── job.ts
```

---

## 8. 개발 우선순위 (Claude Code 작업 순서)

| 순서 | 작업 | 비고 |
|------|------|------|
| 1 | 프로젝트 초기 세팅 (Next.js + Tailwind + Pretendard) | |
| 2 | `types/`, `constants/`, `lib/api.ts` 작성 | 데이터 구조 먼저 |
| 3 | `useSurvey.ts` 훅 구현 (조건부 로직 포함) | |
| 4 | 설문 페이지 UI 구현 | 핵심 기능 |
| 5 | 결과 페이지 — `PersonaCard` + `TraitBar` | |
| 6 | 결과 페이지 — `JobList` + `JobCard` | |
| 7 | 랜딩 페이지 구현 | |
| 8 | 반응형 처리 (모바일 대응) | |
| 9 | 로딩/에러 상태 처리 | |

---

## 9. 주요 UX 고려사항

- **설문 페이지**: 질문 하나씩 전체 화면 포커스. 배경 흐림 효과로 현재 질문에 집중 유도
- **조건부 질문**: Q2, Q3가 노출되지 않을 경우 진행 단계 표시(프로그레스바)도 동적으로 조정
- **공고 카드**: "공고 보기" 버튼 클릭 시 `detail_url`로 새 탭 이동. 카드 자체는 클릭 인터랙션 없음
- **로딩 상태**: 결과 페이지 진입 시 스켈레톤 UI 표시 (API 응답 대기)
- **에러 처리**: API 실패 시 재시도 버튼 + 안내 문구 표시
- **캐릭터 영역**: 현재는 플레이스홀더 박스. 추후 `cluster_id`에 매핑되는 이미지 URL을 `CLUSTER_TRAITS`에 추가하여 교체

---

## 10. 향후 확장 포인트

- `CLUSTER_TRAITS`에 LLM 생성 캐릭터 이미지 URL 필드 추가
- 지역 필터 추가 (`region`은 Response에 이미 포함 — Request에 필터 파라미터는 없으므로, 프론트 클라이언트 사이드 필터링 or 백엔드 파라미터 추가 협의)
- 즐겨찾기/북마크 기능 (localStorage)
- 결과 공유 기능 (카카오톡 공유 등)
