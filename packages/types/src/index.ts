export interface Project {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export type Marketplace = "amazon" | "ebay" | "tiktok";

export type ResearchSessionStatus = "pending" | "running" | "completed" | "failed";

export interface ResearchSession {
  id: string;
  project_id: string;
  marketplace: Marketplace;
  status: ResearchSessionStatus;
  created_at: string;
  updated_at: string;
}

export interface ResearchResult {
  id: string;
  research_session_id: string;
  opportunity_score: number;
  demand_level: string;
  competition_level: string;
  profit_level: string;
  summary: string;
  created_at: string;
  updated_at: string;
}
