import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { createProject, listProjects } from "@/lib/api/projects";
import { getResearchResult } from "@/lib/api/researchResults";
import { createResearchSession, listResearchSessions } from "@/lib/api/researchSessions";

import ProjectsPage from "./page";

vi.mock("@/lib/api/projects", () => ({
  createProject: vi.fn(),
  listProjects: vi.fn(),
}));

vi.mock("@/lib/api/researchSessions", () => ({
  createResearchSession: vi.fn(),
  listResearchSessions: vi.fn(),
}));

vi.mock("@/lib/api/researchResults", () => ({
  getResearchResult: vi.fn(),
}));

const mockedCreateProject = vi.mocked(createProject);
const mockedListProjects = vi.mocked(listProjects);
const mockedCreateResearchSession = vi.mocked(createResearchSession);
const mockedListResearchSessions = vi.mocked(listResearchSessions);
const mockedGetResearchResult = vi.mocked(getResearchResult);

const CREATED_PROJECT = {
  id: "11111111-1111-1111-1111-111111111111",
  name: "Kitchen Research",
  created_at: "2026-07-22T00:00:00Z",
  updated_at: "2026-07-22T00:00:00Z",
};

const CREATED_SESSION = {
  id: "22222222-2222-2222-2222-222222222222",
  project_id: CREATED_PROJECT.id,
  marketplace: "amazon" as const,
  status: "pending" as const,
  created_at: "2026-07-22T00:00:00Z",
  updated_at: "2026-07-22T00:00:00Z",
};

beforeEach(() => {
  mockedCreateProject.mockReset();
  mockedListProjects.mockReset();
  mockedCreateResearchSession.mockReset();
  mockedListResearchSessions.mockReset();
  mockedGetResearchResult.mockReset();

  mockedListProjects.mockResolvedValue([]);
  mockedListResearchSessions.mockResolvedValue([]);
});

async function createProjectViaUi() {
  mockedCreateProject.mockResolvedValue(CREATED_PROJECT);

  const user = userEvent.setup();
  render(<ProjectsPage />);

  await screen.findByText("No projects yet. Create one above.");

  await user.type(screen.getByLabelText("Project name"), "Kitchen Research");
  await user.click(screen.getByRole("button", { name: "Create" }));

  await screen.findByRole("heading", { name: "Kitchen Research", level: 2 });

  return user;
}

async function startResearchViaUi() {
  mockedCreateResearchSession.mockResolvedValue(CREATED_SESSION);

  const user = await createProjectViaUi();

  await user.selectOptions(screen.getByLabelText("Marketplace"), "amazon");
  await user.click(screen.getByRole("button", { name: "Start Research" }));
  await screen.findByText("pending");

  return user;
}

describe("ProjectsPage", () => {
  it("loads and lists existing projects on mount", async () => {
    mockedListProjects.mockResolvedValue([CREATED_PROJECT]);

    render(<ProjectsPage />);

    expect(await screen.findByRole("button", { name: "Kitchen Research" })).toBeInTheDocument();
  });

  it("shows an error message when loading projects fails", async () => {
    mockedListProjects.mockRejectedValue(new Error("network error"));

    render(<ProjectsPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Something went wrong while loading projects. Please try again."
    );
  });

  it("shows a validation error and does not submit when the name is too short", async () => {
    const user = userEvent.setup();
    render(<ProjectsPage />);

    await user.type(screen.getByLabelText("Project name"), "ab");
    await user.click(screen.getByRole("button", { name: "Create" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Project name must be at least 3 characters."
    );
    expect(mockedCreateProject).not.toHaveBeenCalled();
  });

  it("shows a loading state and selects the created project on submit", async () => {
    let resolveCreateProject: (value: typeof CREATED_PROJECT) => void = () => {};
    mockedCreateProject.mockReturnValue(
      new Promise((resolve) => {
        resolveCreateProject = resolve;
      })
    );

    const user = userEvent.setup();
    render(<ProjectsPage />);
    await screen.findByText("No projects yet. Create one above.");

    await user.type(screen.getByLabelText("Project name"), "Kitchen Research");
    await user.click(screen.getByRole("button", { name: "Create" }));

    expect(screen.getByRole("button", { name: "Creating..." })).toBeDisabled();

    resolveCreateProject(CREATED_PROJECT);

    expect(
      await screen.findByRole("heading", { name: "Kitchen Research", level: 2 })
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Kitchen Research" })).toBeInTheDocument();
    expect(mockedCreateProject).toHaveBeenCalledWith("Kitchen Research");
  });

  it("shows an error message when project creation fails", async () => {
    mockedCreateProject.mockRejectedValue(new Error("network error"));

    const user = userEvent.setup();
    render(<ProjectsPage />);
    await screen.findByText("No projects yet. Create one above.");

    await user.type(screen.getByLabelText("Project name"), "Kitchen Research");
    await user.click(screen.getByRole("button", { name: "Create" }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Something went wrong while creating the project. Please try again."
      );
    });
  });

  it("selects an existing project from the list and loads its research sessions", async () => {
    mockedListProjects.mockResolvedValue([CREATED_PROJECT]);
    mockedListResearchSessions.mockResolvedValue([CREATED_SESSION]);

    const user = userEvent.setup();
    render(<ProjectsPage />);

    await user.click(await screen.findByRole("button", { name: "Kitchen Research" }));

    expect(
      await screen.findByRole("heading", { name: "Kitchen Research", level: 2 })
    ).toBeInTheDocument();
    expect(await screen.findByText("pending")).toBeInTheDocument();
    expect(mockedListResearchSessions).toHaveBeenCalledWith(CREATED_PROJECT.id);
  });

  it("shows an error message when loading research sessions fails", async () => {
    mockedListProjects.mockResolvedValue([CREATED_PROJECT]);
    mockedListResearchSessions.mockRejectedValue(new Error("network error"));

    const user = userEvent.setup();
    render(<ProjectsPage />);

    await user.click(await screen.findByRole("button", { name: "Kitchen Research" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Something went wrong while loading research sessions. Please try again."
    );
  });

  it("shows a validation error and does not start research when marketplace is blank", async () => {
    const user = await createProjectViaUi();

    await user.click(screen.getByRole("button", { name: "Start Research" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Marketplace is required.");
    expect(mockedCreateResearchSession).not.toHaveBeenCalled();
  });

  it("starts research and displays the created session", async () => {
    await startResearchViaUi();

    const sessionItem = await screen.findByText("pending");
    expect(sessionItem.closest("li")).toHaveTextContent("Amazon");
    expect(mockedCreateResearchSession).toHaveBeenCalledWith(CREATED_PROJECT.id, "amazon");
  });

  it("shows an error message when starting research fails", async () => {
    mockedCreateResearchSession.mockRejectedValue(new Error("network error"));

    const user = await createProjectViaUi();

    await user.selectOptions(screen.getByLabelText("Marketplace"), "amazon");
    await user.click(screen.getByRole("button", { name: "Start Research" }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Something went wrong while starting research. Please try again."
      );
    });
  });

  it("loads and displays the research result when View Result is clicked, and refreshes the session status", async () => {
    mockedGetResearchResult.mockResolvedValue({
      id: "33333333-3333-3333-3333-333333333333",
      research_session_id: CREATED_SESSION.id,
      opportunity_score: 84,
      demand_level: "high",
      competition_level: "medium",
      profit_level: "good",
      summary: "This product shows promising demand with manageable competition.",
      created_at: "2026-07-22T00:00:00Z",
      updated_at: "2026-07-22T00:00:00Z",
    });

    const user = await startResearchViaUi();

    mockedListResearchSessions.mockResolvedValue([{ ...CREATED_SESSION, status: "completed" }]);
    await user.click(screen.getByRole("button", { name: "View Result" }));

    expect(await screen.findByText("84")).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText("Medium")).toBeInTheDocument();
    expect(screen.getByText("Good")).toBeInTheDocument();
    expect(
      screen.getByText("This product shows promising demand with manageable competition.")
    ).toBeInTheDocument();
    expect(mockedGetResearchResult).toHaveBeenCalledWith(CREATED_SESSION.id);
    expect(screen.queryByRole("button", { name: "View Result" })).not.toBeInTheDocument();
    expect(await screen.findByText("completed")).toBeInTheDocument();
  });

  it("shows an error message when loading the research result fails", async () => {
    mockedGetResearchResult.mockRejectedValue(new Error("network error"));

    const user = await startResearchViaUi();

    await user.click(screen.getByRole("button", { name: "View Result" }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Something went wrong while loading the research result. Please try again."
      );
    });
    expect(screen.getByRole("button", { name: "View Result" })).toBeInTheDocument();
  });
});
