// cluster_id → cluster_name 매핑은 백엔드 API 응답 기준
// 0: 안정적 사무/CS형
// 1: 고수익 단기/노무형
// 2: 일반 파트타임 서비스형
// 3: 정규 식음료/매장관리형

export const CLUSTER_TRAITS: Record<number, {
  description: string;
  traits: { label: string; value: number }[];
}> = {
  0: {
    description: "조용한 실내에서 집중하며 안정을 추구하는 스타일",
    traits: [
      { label: "에너지력", value: 30 },
      { label: "유연성",   value: 30 },
      { label: "집중력",   value: 90 },
      { label: "사교성",   value: 70 },
    ],
  },
  1: {
    description: "빠르게 벌고 자유롭게 쉬는 스타일",
    traits: [
      { label: "에너지력", value: 95 },
      { label: "유연성",   value: 80 },
      { label: "집중력",   value: 40 },
      { label: "사교성",   value: 30 },
    ],
  },
  2: {
    description: "유연하게, 내 페이스로 시작하는 스타일",
    traits: [
      { label: "에너지력", value: 40 },
      { label: "유연성",   value: 90 },
      { label: "집중력",   value: 50 },
      { label: "사교성",   value: 60 },
    ],
  },
  3: {
    description: "든든한 보장 속에서 전문성을 쌓는 스타일",
    traits: [
      { label: "에너지력", value: 70 },
      { label: "유연성",   value: 40 },
      { label: "집중력",   value: 75 },
      { label: "사교성",   value: 80 },
    ],
  },
};
