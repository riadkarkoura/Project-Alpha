"use client";

import { useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createProject, listProjects } from "@/lib/api/projects";
import { getResearchResult } from "@/lib/api/researchResults";
import { createResearchSession, listResearchSessions } from "@/lib/api/researchSessions";
import type { Marketplace, Project, ResearchResult, ResearchSession } from "@project-alpha/types";

const MIN_NAME_LENGTH = 3;
const MAX_NAME_LENGTH = 100;

const MARKETPLACE_OPTIONS: { value: Marketplace; label: string }[] = [
  { value: "amazon", label: "Amazon" },
  { value: "ebay", label: "eBay" },
  { value: "tiktok", label: "TikTok" },
];

function validateName(name: string): string | null {
  const trimmed = name.trim();
  if (trimmed.length < MIN_NAME_LENGTH) {
    return `Project name must be at least ${MIN_NAME_LENGTH} characters.`;
  }
  if (trimmed.length > MAX_NAME_LENGTH) {
    return `Project name must be at most ${MAX_NAME_LENGTH} characters.`;
  }
  return null;
}

function validateMarketplace(marketplace: Marketplace | ""): string | null {
  if (marketplace === "") {
    return "Marketplace is required.";
  }
  return null;
}

function capitalize(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export default function ProjectsPage() {
  const [name, setName] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [loadProjectsError, setLoadProjectsError] = useState<string | null>(null);

  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  const [marketplace, setMarketplace] = useState<Marketplace | "">("");
  const [marketplaceError, setMarketplaceError] = useState<string | null>(null);
  const [isStartingResearch, setIsStartingResearch] = useState(false);
  const [researchError, setResearchError] = useState<string | null>(null);

  const [researchSessions, setResearchSessions] = useState<ResearchSession[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [loadSessionsError, setLoadSessionsError] = useState<string | null>(null);

  const [researchResults, setResearchResults] = useState<Record<string, ResearchResult>>({});
  const [loadingResultIds, setLoadingResultIds] = useState<Set<string>>(new Set());
  const [resultErrors, setResultErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    let cancelled = false;

    async function loadProjects() {
      setIsLoadingProjects(true);
      setLoadProjectsError(null);

      try {
        const loaded = await listProjects();
        if (!cancelled) {
          setProjects(loaded);
        }
      } catch {
        if (!cancelled) {
          setLoadProjectsError("Something went wrong while loading projects. Please try again.");
        }
      } finally {
        if (!cancelled) {
          setIsLoadingProjects(false);
        }
      }
    }

    void loadProjects();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedProjectId) {
      return;
    }

    let cancelled = false;

    async function loadSessions(projectId: string) {
      setIsLoadingSessions(true);
      setLoadSessionsError(null);

      try {
        const sessions = await listResearchSessions(projectId);
        if (!cancelled) {
          setResearchSessions(sessions);
        }
      } catch {
        if (!cancelled) {
          setLoadSessionsError(
            "Something went wrong while loading research sessions. Please try again."
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoadingSessions(false);
        }
      }
    }

    void loadSessions(selectedProjectId);

    return () => {
      cancelled = true;
    };
  }, [selectedProjectId]);

  const selectedProject = projects.find((project) => project.id === selectedProjectId) ?? null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const error = validateName(name);
    setValidationError(error);
    if (error) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const project = await createProject(name.trim());
      setProjects((current) => [project, ...current]);
      setSelectedProjectId(project.id);
      setName("");
    } catch {
      setSubmitError("Something went wrong while creating the project. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleStartResearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedProject) {
      return;
    }

    const error = validateMarketplace(marketplace);
    setMarketplaceError(error);
    if (error || marketplace === "") {
      return;
    }

    setIsStartingResearch(true);
    setResearchError(null);

    try {
      const session = await createResearchSession(selectedProject.id, marketplace);
      setResearchSessions((sessions) => [session, ...sessions]);
      setMarketplace("");
    } catch {
      setResearchError("Something went wrong while starting research. Please try again.");
    } finally {
      setIsStartingResearch(false);
    }
  }

  async function handleViewResult(sessionId: string) {
    setLoadingResultIds((ids) => new Set(ids).add(sessionId));
    setResultErrors((errors) => {
      const next = { ...errors };
      delete next[sessionId];
      return next;
    });

    try {
      const result = await getResearchResult(sessionId);
      setResearchResults((results) => ({ ...results, [sessionId]: result }));

      if (selectedProjectId) {
        const refreshed = await listResearchSessions(selectedProjectId);
        setResearchSessions(refreshed);
      }
    } catch {
      setResultErrors((errors) => ({
        ...errors,
        [sessionId]: "Something went wrong while loading the research result. Please try again.",
      }));
    } finally {
      setLoadingResultIds((ids) => {
        const next = new Set(ids);
        next.delete(sessionId);
        return next;
      });
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-md flex-col gap-6 p-8">
      <h1 className="text-2xl font-semibold">Projects</h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="project-name">Project name</Label>
          <Input
            id="project-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            aria-invalid={validationError ? true : undefined}
            disabled={isSubmitting}
          />
          {validationError && (
            <p role="alert" className="text-sm text-destructive">
              {validationError}
            </p>
          )}
        </div>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create"}
        </Button>

        {submitError && (
          <p role="alert" className="text-sm text-destructive">
            {submitError}
          </p>
        )}
      </form>

      <div className="flex flex-col gap-2 border-t border-border pt-6">
        <h2 className="text-lg font-semibold">Your projects</h2>

        {isLoadingProjects && <p className="text-sm text-muted-foreground">Loading projects...</p>}

        {loadProjectsError && (
          <p role="alert" className="text-sm text-destructive">
            {loadProjectsError}
          </p>
        )}

        {!isLoadingProjects && !loadProjectsError && projects.length === 0 && (
          <p className="text-sm text-muted-foreground">No projects yet. Create one above.</p>
        )}

        {projects.length > 0 && (
          <ul className="flex flex-col gap-1.5">
            {projects.map((project) => (
              <li key={project.id}>
                <button
                  type="button"
                  onClick={() => setSelectedProjectId(project.id)}
                  aria-current={project.id === selectedProjectId ? "true" : undefined}
                  className="w-full rounded-lg border border-border px-3 py-2 text-left text-sm hover:bg-muted/30 aria-[current=true]:border-ring aria-[current=true]:bg-muted/30"
                >
                  {project.name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {selectedProject && (
        <div className="flex flex-col gap-4 border-t border-border pt-6">
          <h2 className="text-lg font-semibold">{selectedProject.name}</h2>

          <form onSubmit={handleStartResearch} className="flex flex-col gap-4" noValidate>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="marketplace">Marketplace</Label>
              <select
                id="marketplace"
                value={marketplace}
                onChange={(event) => setMarketplace(event.target.value as Marketplace | "")}
                aria-invalid={marketplaceError ? true : undefined}
                disabled={isStartingResearch}
                className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50"
              >
                <option value="" disabled>
                  Select a marketplace
                </option>
                {MARKETPLACE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {marketplaceError && (
                <p role="alert" className="text-sm text-destructive">
                  {marketplaceError}
                </p>
              )}
            </div>

            <Button type="submit" disabled={isStartingResearch}>
              {isStartingResearch ? "Starting..." : "Start Research"}
            </Button>

            {researchError && (
              <p role="alert" className="text-sm text-destructive">
                {researchError}
              </p>
            )}
          </form>

          {isLoadingSessions && (
            <p className="text-sm text-muted-foreground">Loading research sessions...</p>
          )}

          {loadSessionsError && (
            <p role="alert" className="text-sm text-destructive">
              {loadSessionsError}
            </p>
          )}

          {researchSessions.length > 0 && (
            <ul className="flex flex-col gap-3">
              {researchSessions.map((session) => {
                const result = researchResults[session.id];
                const isLoadingResult = loadingResultIds.has(session.id);
                const resultError = resultErrors[session.id];

                return (
                  <li
                    key={session.id}
                    className="flex flex-col gap-2 rounded-lg border border-border px-3 py-2 text-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span>
                        {MARKETPLACE_OPTIONS.find((option) => option.value === session.marketplace)
                          ?.label ?? session.marketplace}
                      </span>
                      <span className="text-muted-foreground">{session.status}</span>
                    </div>

                    {!result && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        disabled={isLoadingResult}
                        onClick={() => handleViewResult(session.id)}
                      >
                        {isLoadingResult ? "Loading..." : "View Result"}
                      </Button>
                    )}

                    {resultError && (
                      <p role="alert" className="text-sm text-destructive">
                        {resultError}
                      </p>
                    )}

                    {result && (
                      <div className="flex flex-col gap-1 rounded-lg border border-border bg-muted/30 p-3">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">Opportunity Score</span>
                          <span>{result.opportunity_score}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="font-medium">Demand</span>
                          <span>{capitalize(result.demand_level)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="font-medium">Competition</span>
                          <span>{capitalize(result.competition_level)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="font-medium">Profit</span>
                          <span>{capitalize(result.profit_level)}</span>
                        </div>
                        <p className="pt-1 text-muted-foreground">{result.summary}</p>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
