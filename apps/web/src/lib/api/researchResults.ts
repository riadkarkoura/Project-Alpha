import type { ResearchResult } from "@project-alpha/types";

import { apiFetch } from "@/lib/api/client";

export async function getResearchResult(researchSessionId: string): Promise<ResearchResult> {
  return apiFetch<ResearchResult>(`/api/v1/research-sessions/${researchSessionId}/research-result`);
}
