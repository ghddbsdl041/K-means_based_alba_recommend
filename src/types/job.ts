export interface Job {
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

export interface RecommendRequest {
  q1_answer: "A" | "B";
  q2_answer?: "A" | "B";
  q3_answer?: "A" | "B";
  q4_answer: "A" | "B";
  q5_answer: "A" | "B";
  limit: number;
}
