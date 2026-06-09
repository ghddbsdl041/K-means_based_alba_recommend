export interface ClusterTheme {
  badge: string;
  name: string;
  description: string;
  tagBg: string;
  summaryBox: string;
  summaryText: string;
  summaryStrong: string;
  highlightCard: string;
  highlightBorder: string;
  highlightTag: string;
  barFrom: string;
  barTo: string;
  button: string;
}

export const CLUSTER_THEMES: Record<number, ClusterTheme> = {
  // 안정적 사무/CS형 — 차분한 인디고
  0: {
    badge:         "bg-indigo-100 text-indigo-600",
    name:          "text-indigo-700",
    description:   "text-indigo-400",
    tagBg:         "bg-indigo-100 text-indigo-600",
    summaryBox:    "bg-indigo-50 border-indigo-100",
    summaryText:   "text-indigo-500",
    summaryStrong: "text-indigo-700",
    highlightCard: "bg-indigo-50/70",
    highlightBorder: "border-indigo-200/60 shadow-indigo-100",
    highlightTag:  "bg-indigo-100 text-indigo-600",
    barFrom: "#6366F1",
    barTo:   "#A5B4FC",
    button:  "bg-indigo-600 hover:bg-indigo-700 shadow-indigo-200",
  },
  // 고수익 단기/노무형 — 활기찬 오렌지
  1: {
    badge:         "bg-orange-100 text-orange-600",
    name:          "text-orange-600",
    description:   "text-orange-400",
    tagBg:         "bg-orange-100 text-orange-600",
    summaryBox:    "bg-orange-50 border-orange-100",
    summaryText:   "text-orange-500",
    summaryStrong: "text-orange-700",
    highlightCard: "bg-orange-50/70",
    highlightBorder: "border-orange-200/60 shadow-orange-100",
    highlightTag:  "bg-orange-100 text-orange-600",
    barFrom: "#F97316",
    barTo:   "#FED7AA",
    button:  "bg-orange-500 hover:bg-orange-600 shadow-orange-200",
  },
  // 일반 파트타임 서비스형 — 친근한 에메랄드
  2: {
    badge:         "bg-emerald-100 text-emerald-600",
    name:          "text-emerald-700",
    description:   "text-emerald-400",
    tagBg:         "bg-emerald-100 text-emerald-600",
    summaryBox:    "bg-emerald-50 border-emerald-100",
    summaryText:   "text-emerald-500",
    summaryStrong: "text-emerald-700",
    highlightCard: "bg-emerald-50/70",
    highlightBorder: "border-emerald-200/60 shadow-emerald-100",
    highlightTag:  "bg-emerald-100 text-emerald-600",
    barFrom: "#10B981",
    barTo:   "#6EE7B7",
    button:  "bg-emerald-500 hover:bg-emerald-600 shadow-emerald-200",
  },
  // 정규 식음료/매장관리형 — 따뜻한 로즈
  3: {
    badge:         "bg-rose-100 text-rose-600",
    name:          "text-rose-700",
    description:   "text-rose-400",
    tagBg:         "bg-rose-100 text-rose-600",
    summaryBox:    "bg-rose-50 border-rose-100",
    summaryText:   "text-rose-500",
    summaryStrong: "text-rose-700",
    highlightCard: "bg-rose-50/70",
    highlightBorder: "border-rose-200/60 shadow-rose-100",
    highlightTag:  "bg-rose-100 text-rose-600",
    barFrom: "#F43F5E",
    barTo:   "#FDA4AF",
    button:  "bg-rose-500 hover:bg-rose-600 shadow-rose-200",
  },
};

export function getTheme(clusterId: number): ClusterTheme {
  return CLUSTER_THEMES[clusterId] ?? CLUSTER_THEMES[0];
}
