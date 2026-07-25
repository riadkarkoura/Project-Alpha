import type { Marketplace, ResearchSession } from "@project-alpha/types";

import { apiFetch } from "@/lib/api/client";

export async function createResearchSession(
  projectId: string,
  marketplace: Marketplace
): Promise<ResearchSession> {
  return apiFetch<ResearchSession>(`/api/v1/projects/${projectId}/research-sessions`, {
    method: "POST",
    body: JSON.stringify({ marketplace }),
  });
}

export async function listResearchSessions(projectId: string): Promise<ResearchSession[]> {
  return apiFetch<ResearchSession[]>(`/api/v1/projects/${projectId}/research-sessions`);
}
