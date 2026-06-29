import type { Job, RecommendRequest } from "../types/job";
import type { SurveyAnswers } from "../types/survey";

const API_URL = "https://alba-backend-1037394136554.us-central1.run.app/api/recommend";

export async function fetchRecommendations(answers: SurveyAnswers): Promise<Job[]> {
  if (!answers.Q1 || !answers.Q4 || !answers.Q5) {
    throw new Error("필수 답변이 누락되었습니다.");
  }

  const body: RecommendRequest = {
    q1_answer: answers.Q1,
    q4_answer: answers.Q4,
    q5_answer: answers.Q5,
    limit: 100,
  };

  if (answers.Q1 === "B" && answers.Q2) body.q2_answer = answers.Q2;
  if (answers.Q2 === "B" && answers.Q3) body.q3_answer = answers.Q3;

  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error("추천 공고를 불러오지 못했습니다.");
  return res.json();
}
