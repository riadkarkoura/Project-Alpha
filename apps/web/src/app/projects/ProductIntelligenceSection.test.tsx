import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  createProductIntelligence,
  deleteProductIntelligence,
  generateProductDescription,
  listProductIntelligence,
  markProductIntelligenceReadyForPublishing,
  updateProductIntelligence,
} from "@/lib/api/productIntelligence";

import { ProductIntelligenceSection } from "./ProductIntelligenceSection";

vi.mock("@/lib/api/productIntelligence", () => ({
  createProductIntelligence: vi.fn(),
  listProductIntelligence: vi.fn(),
  updateProductIntelligence: vi.fn(),
  deleteProductIntelligence: vi.fn(),
  markProductIntelligenceReadyForPublishing: vi.fn(),
  generateProductDescription: vi.fn(),
}));

const mockedCreate = vi.mocked(createProductIntelligence);
const mockedList = vi.mocked(listProductIntelligence);
const mockedDelete = vi.mocked(deleteProductIntelligence);
const mockedMarkReady = vi.mocked(markProductIntelligenceReadyForPublishing);
const mockedGenerate = vi.mocked(generateProductDescription);
const mockedUpdate = vi.mocked(updateProductIntelligence);

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

const BASE_PRODUCT = {
  id: "44444444-4444-4444-4444-444444444444",
  project_id: PROJECT_ID,
  research_session_id: null,
  title: "Bamboo Cutting Board",
  subtitle: null,
  description: null,
  features: [],
  specifications: [],
  category: null,
  tags: [],
  keywords: [],
  seo: { meta_title: null, meta_description: null, slug: null },
  pricing: null,
  images: [],
  publishing: { published_channels: [], published_at: null },
  status: "draft" as const,
  created_at: "2026-07-22T00:00:00Z",
  updated_at: "2026-07-22T00:00:00Z",
};

beforeEach(() => {
  mockedCreate.mockReset();
  mockedList.mockReset();
  mockedDelete.mockReset();
  mockedMarkReady.mockReset();
  mockedGenerate.mockReset();
  mockedUpdate.mockReset();

  mockedList.mockResolvedValue([]);
});

describe("ProductIntelligenceSection", () => {
  it("loads and displays existing products", async () => {
    mockedList.mockResolvedValue([BASE_PRODUCT]);

    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);

    expect(await screen.findByText("Bamboo Cutting Board")).toBeInTheDocument();
    expect(mockedList).toHaveBeenCalledWith(PROJECT_ID);
  });

  it("shows an error message when loading products fails", async () => {
    mockedList.mockRejectedValue(new Error("network error"));

    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Something went wrong while loading products. Please try again."
    );
  });

  it("shows a validation error and does not submit when the title is too short", async () => {
    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("No products yet. Add one above.");

    await user.type(screen.getByLabelText("Title"), "ab");
    await user.click(screen.getByRole("button", { name: "Add Product" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Product title must be at least 3 characters."
    );
    expect(mockedCreate).not.toHaveBeenCalled();
  });

  it("creates a product and displays it in the list", async () => {
    mockedCreate.mockResolvedValue(BASE_PRODUCT);

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("No products yet. Add one above.");

    await user.type(screen.getByLabelText("Title"), "Bamboo Cutting Board");
    await user.click(screen.getByRole("button", { name: "Add Product" }));

    expect(await screen.findByText("Bamboo Cutting Board")).toBeInTheDocument();
    expect(mockedCreate).toHaveBeenCalledWith(
      PROJECT_ID,
      expect.objectContaining({ title: "Bamboo Cutting Board" })
    );
  });

  it("shows an error message when creating a product fails", async () => {
    mockedCreate.mockRejectedValue(new Error("network error"));

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("No products yet. Add one above.");

    await user.type(screen.getByLabelText("Title"), "Bamboo Cutting Board");
    await user.click(screen.getByRole("button", { name: "Add Product" }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Something went wrong while creating the product. Please try again."
      );
    });
  });

  it("marks a draft product ready for publishing", async () => {
    mockedList.mockResolvedValue([BASE_PRODUCT]);
    mockedMarkReady.mockResolvedValue({ ...BASE_PRODUCT, status: "ready_for_publishing" });

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("Bamboo Cutting Board");

    await user.click(screen.getByRole("button", { name: "Mark Ready for Publishing" }));

    expect(await screen.findByText("Ready for publishing")).toBeInTheDocument();
    expect(mockedMarkReady).toHaveBeenCalledWith(BASE_PRODUCT.id);
  });

  it("shows an error when marking ready for publishing fails", async () => {
    mockedList.mockResolvedValue([BASE_PRODUCT]);
    mockedMarkReady.mockRejectedValue(new Error("unprocessable"));

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("Bamboo Cutting Board");

    await user.click(screen.getByRole("button", { name: "Mark Ready for Publishing" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Could not mark this product ready for publishing."
    );
  });

  it("deletes a product and removes it from the list", async () => {
    mockedList.mockResolvedValue([BASE_PRODUCT]);
    mockedDelete.mockResolvedValue(undefined);

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("Bamboo Cutting Board");

    await user.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() => {
      expect(screen.queryByText("Bamboo Cutting Board")).not.toBeInTheDocument();
    });
    expect(mockedDelete).toHaveBeenCalledWith(BASE_PRODUCT.id);
  });

  it("generates a draft description without saving it", async () => {
    mockedList.mockResolvedValue([BASE_PRODUCT]);
    mockedGenerate.mockResolvedValue({
      product_id: BASE_PRODUCT.id,
      description: "A lovely bamboo board.",
    });

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("Bamboo Cutting Board");

    await user.click(screen.getByRole("button", { name: "Generate Description" }));

    expect(await screen.findByText("Generated description (draft)")).toBeInTheDocument();
    expect(screen.getByText("A lovely bamboo board.")).toBeInTheDocument();
    expect(screen.getByText("No description yet.")).toBeInTheDocument(); // saved value unchanged
    expect(mockedUpdate).not.toHaveBeenCalled();
  });

  it("shows an error when generating a description fails", async () => {
    mockedList.mockResolvedValue([BASE_PRODUCT]);
    mockedGenerate.mockRejectedValue(new Error("network error"));

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("Bamboo Cutting Board");

    await user.click(screen.getByRole("button", { name: "Generate Description" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Something went wrong while generating a description. Please try again."
    );
  });

  it("accepts a generated draft and saves it via the update endpoint", async () => {
    mockedList.mockResolvedValue([BASE_PRODUCT]);
    mockedGenerate.mockResolvedValue({
      product_id: BASE_PRODUCT.id,
      description: "A lovely bamboo board.",
    });
    mockedUpdate.mockResolvedValue({ ...BASE_PRODUCT, description: "A lovely bamboo board." });

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("Bamboo Cutting Board");

    await user.click(screen.getByRole("button", { name: "Generate Description" }));
    await screen.findByText("Generated description (draft)");
    await user.click(screen.getByRole("button", { name: "Accept" }));

    expect(mockedUpdate).toHaveBeenCalledWith(
      BASE_PRODUCT.id,
      expect.objectContaining({ title: "Bamboo Cutting Board", description: "A lovely bamboo board." })
    );
    await waitFor(() => {
      expect(screen.queryByText("Generated description (draft)")).not.toBeInTheDocument();
    });
  });

  it("discards a generated draft without calling the API", async () => {
    mockedList.mockResolvedValue([BASE_PRODUCT]);
    mockedGenerate.mockResolvedValue({
      product_id: BASE_PRODUCT.id,
      description: "A lovely bamboo board.",
    });

    const user = userEvent.setup();
    render(<ProductIntelligenceSection projectId={PROJECT_ID} />);
    await screen.findByText("Bamboo Cutting Board");

    await user.click(screen.getByRole("button", { name: "Generate Description" }));
    await screen.findByText("Generated description (draft)");
    await user.click(screen.getByRole("button", { name: "Discard" }));

    expect(screen.queryByText("Generated description (draft)")).not.toBeInTheDocument();
    expect(mockedUpdate).not.toHaveBeenCalled();
  });
});
