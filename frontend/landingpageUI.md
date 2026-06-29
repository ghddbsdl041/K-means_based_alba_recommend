현재 프로젝트에 React + Tailwind CSS + Framer Motion 기반의 히어로 섹션 컴포넌트를 만들어줘.

## 작업 목표
`src/components/HeroSection.tsx` 파일을 새로 생성해줘.
기존 프로젝트 구조(package.json, tailwind.config, tsconfig 등)를 먼저 확인하고,
framer-motion이 설치되어 있지 않으면 설치까지 진행해줘.

---

## 레이아웃 구조
- 데스크탑: 좌우 2분할 (left 50% 텍스트 | right 50% 슬라이더)
- 모바일: 위아래 1열 (텍스트 → 슬라이더 순)
- 배경: #F0F4FF (연한 블루-그레이)

---

## 왼쪽 섹션 (텍스트 + 버튼)
순서대로 배치:

1. 뱃지
   - 텍스트: "Real-time AI Crawling Engine"
   - 스타일: 배경 #EDE9FE (연보라), 텍스트 #6D28D9, 폰트 12px, border-radius 999px, padding 4px 12px

2. 메인 타이틀 (font-size: 40px, font-weight: 800, line-height: 1.3)
   - 일반 텍스트: "실시간 AI 크롤링으로 찾는 나만의 "
   - 강조 텍스트: "딱 맞는 알바" → 색상 #2563EB (파란색)

3. 서브 텍스트 (font-size: 15px, color: #6B7280, margin-top: 16px)
   - "수만 개의 알바 사이트를 실시간으로 분석하여, 당신의 성향과 능력에 맞는 최적의 일자리를 매칭해드립니다."

4. 버튼 2개 (margin-top: 32px, gap: 12px, flex-wrap: wrap)
   - Primary: "내 유형 진단하고 매칭 시작하기"
     배경 #2563EB, 텍스트 white, border-radius 8px, padding 12px 24px, font-weight 600
   - Ghost: "서비스 소개 보기"
     배경 transparent, border 1.5px solid #2563EB, 텍스트 #2563EB, 동일 padding

---

## 오른쪽 섹션 (캐릭터 카드 슬라이더)

### 슬라이더 동작 방식
- 한 번에 **2장**의 카드가 보임 (현재 카드 + 다음 카드의 일부)
- 4초마다 자동으로 다음 카드로 전환 (무한 루프)
- 전환 애니메이션: Framer Motion `AnimatePresence` + `x` 방향 slide (easing: easeInOut, duration: 0.5s)
- 하단에 dot indicator 4개 (현재 활성 dot: #2563EB, 나머지: #D1D5DB)

### 캐릭터 카드 데이터 (4종)
아래 배열을 컴포넌트 상단에 상수로 선언해줘:

```ts
const CHARACTER_CARDS = [
  이미지는 src/assets/{이미지들} 사용해.
];
```

### 카드 1장 스타일
- 배경: white, border-radius: 20px, box-shadow: 0 4px 20px rgba(0,0,0,0.08)
- 이미지: `aspect-square`, `object-contain`, width 100%, 캐릭터가 잘리지 않게
- 이미지 하단에 label 텍스트: font-size 13px, color #374151, text-align center, padding 12px
- 이미지 로드 실패 시 회색 placeholder 박스로 대체 (onError 처리)

---

## 폰트
Tailwind config에 Pretendard 폰트가 없으면 `index.css`에 아래 import를 추가해줘:
```css
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
```
font-family를 'Pretendard', sans-serif로 hero 섹션 전체에 적용.

---

## 완료 후 체크리스트
- [ ] `HeroSection.tsx` 생성됨
- [ ] framer-motion import 정상 작동
- [ ] 모바일 반응형 확인 (Tailwind `md:` breakpoint 기준)
- [ ] dot indicator가 현재 슬라이드와 동기화됨
- [ ] `App.tsx` 또는 메인 페이지에 `<HeroSection />` import 및 렌더링 추가