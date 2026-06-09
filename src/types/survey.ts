export type AnswerValue = "A" | "B";

export interface Question {
  id: "Q1" | "Q2" | "Q3" | "Q4" | "Q5";
  text: string;
  optionA: { label: string; description: string };
  optionB: { label: string; description: string };
  condition?: { questionId: string; requiredValue: AnswerValue };
  required: boolean;
}

export type SurveyAnswers = Partial<Record<"Q1" | "Q2" | "Q3" | "Q4" | "Q5", AnswerValue>>;

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
