import type { ProductIntelligence } from "@project-alpha/types";

import { apiFetch } from "@/lib/api/client";

export interface ProductIntelligenceInput {
  title: string;
  subtitle?: string;
  description?: string;
  category?: string;
  tags?: string[];
  pricing?: { amount: string; currency: string };
}

export async function createProductIntelligence(
  projectId: string,
  input: ProductIntelligenceInput
): Promise<ProductIntelligence> {
  return apiFetch<ProductIntelligence>(`/api/v1/projects/${projectId}/product-intelligence`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function listProductIntelligence(projectId: string): Promise<ProductIntelligence[]> {
  return apiFetch<ProductIntelligence[]>(`/api/v1/projects/${projectId}/product-intelligence`);
}

export async function updateProductIntelligence(
  productId: string,
  input: ProductIntelligenceInput
): Promise<ProductIntelligence> {
  return apiFetch<ProductIntelligence>(`/api/v1/product-intelligence/${productId}`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export async function deleteProductIntelligence(productId: string): Promise<void> {
  await apiFetch<void>(`/api/v1/product-intelligence/${productId}`, {
    method: "DELETE",
  });
}

export async function markProductIntelligenceReadyForPublishing(
  productId: string
): Promise<ProductIntelligence> {
  return apiFetch<ProductIntelligence>(
    `/api/v1/product-intelligence/${productId}/mark-ready-for-publishing`,
    { method: "POST" }
  );
}
