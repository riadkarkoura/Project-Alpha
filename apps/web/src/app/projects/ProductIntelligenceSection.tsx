"use client";

import { useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createProductIntelligence,
  deleteProductIntelligence,
  generateProductDescription,
  listProductIntelligence,
  markProductIntelligenceReadyForPublishing,
  updateProductIntelligence,
} from "@/lib/api/productIntelligence";
import type { ProductIntelligence } from "@project-alpha/types";

const MIN_TITLE_LENGTH = 3;

function validateTitle(title: string): string | null {
  if (title.trim().length < MIN_TITLE_LENGTH) {
    return `Product title must be at least ${MIN_TITLE_LENGTH} characters.`;
  }
  return null;
}

function parseTags(value: string): string[] {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0);
}

const STATUS_LABELS: Record<ProductIntelligence["status"], string> = {
  draft: "Draft",
  ready_for_publishing: "Ready for publishing",
  published: "Published",
};

export function ProductIntelligenceSection({ projectId }: { projectId: string }) {
  const [products, setProducts] = useState<ProductIntelligence[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [subtitle, setSubtitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [tags, setTags] = useState("");
  const [priceAmount, setPriceAmount] = useState("");
  const [priceCurrency, setPriceCurrency] = useState("USD");
  const [titleError, setTitleError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [actionErrors, setActionErrors] = useState<Record<string, string>>({});
  const [pendingActionIds, setPendingActionIds] = useState<Set<string>>(new Set());

  // Generated descriptions are drafts only, kept in local state until the
  // user explicitly accepts (saved via the normal update call) or discards
  // (just cleared here) - generation never touches the saved product.
  const [draftDescriptions, setDraftDescriptions] = useState<Record<string, string>>({});
  const [generatingIds, setGeneratingIds] = useState<Set<string>>(new Set());
  const [acceptingIds, setAcceptingIds] = useState<Set<string>>(new Set());
  const [draftErrors, setDraftErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setLoadError(null);

      try {
        const loaded = await listProductIntelligence(projectId);
        if (!cancelled) {
          setProducts(loaded);
        }
      } catch {
        if (!cancelled) {
          setLoadError("Something went wrong while loading products. Please try again.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [projectId]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const error = validateTitle(title);
    setTitleError(error);
    if (error) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const product = await createProductIntelligence(projectId, {
        title: title.trim(),
        subtitle: subtitle.trim() || undefined,
        description: description.trim() || undefined,
        category: category.trim() || undefined,
        tags: parseTags(tags),
        pricing: priceAmount.trim()
          ? { amount: priceAmount.trim(), currency: priceCurrency.trim() || "USD" }
          : undefined,
      });
      setProducts((current) => [product, ...current]);
      setTitle("");
      setSubtitle("");
      setDescription("");
      setCategory("");
      setTags("");
      setPriceAmount("");
    } catch {
      setSubmitError("Something went wrong while creating the product. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleMarkReady(productId: string) {
    setPendingActionIds((ids) => new Set(ids).add(productId));
    setActionErrors((errors) => {
      const next = { ...errors };
      delete next[productId];
      return next;
    });

    try {
      const updated = await markProductIntelligenceReadyForPublishing(productId);
      setProducts((current) => current.map((p) => (p.id === productId ? updated : p)));
    } catch {
      setActionErrors((errors) => ({
        ...errors,
        [productId]:
          "Could not mark this product ready for publishing. It may be missing a description or price.",
      }));
    } finally {
      setPendingActionIds((ids) => {
        const next = new Set(ids);
        next.delete(productId);
        return next;
      });
    }
  }

  async function handleDelete(productId: string) {
    setPendingActionIds((ids) => new Set(ids).add(productId));

    try {
      await deleteProductIntelligence(productId);
      setProducts((current) => current.filter((p) => p.id !== productId));
    } catch {
      setActionErrors((errors) => ({
        ...errors,
        [productId]: "Something went wrong while deleting this product. Please try again.",
      }));
      setPendingActionIds((ids) => {
        const next = new Set(ids);
        next.delete(productId);
        return next;
      });
    }
  }

  async function handleGenerateDescription(productId: string) {
    setGeneratingIds((ids) => new Set(ids).add(productId));
    setDraftErrors((errors) => {
      const next = { ...errors };
      delete next[productId];
      return next;
    });

    try {
      const generated = await generateProductDescription(productId);
      setDraftDescriptions((drafts) => ({ ...drafts, [productId]: generated.description }));
    } catch {
      setDraftErrors((errors) => ({
        ...errors,
        [productId]: "Something went wrong while generating a description. Please try again.",
      }));
    } finally {
      setGeneratingIds((ids) => {
        const next = new Set(ids);
        next.delete(productId);
        return next;
      });
    }
  }

  function handleDiscardDescription(productId: string) {
    setDraftDescriptions((drafts) => {
      const next = { ...drafts };
      delete next[productId];
      return next;
    });
  }

  async function handleAcceptDescription(product: ProductIntelligence) {
    const draft = draftDescriptions[product.id];
    if (draft === undefined) {
      return;
    }

    setAcceptingIds((ids) => new Set(ids).add(product.id));
    setDraftErrors((errors) => {
      const next = { ...errors };
      delete next[product.id];
      return next;
    });

    try {
      const updated = await updateProductIntelligence(product.id, {
        title: product.title,
        subtitle: product.subtitle ?? undefined,
        description: draft,
        category: product.category ?? undefined,
        tags: product.tags,
        pricing: product.pricing
          ? { amount: product.pricing.amount, currency: product.pricing.currency }
          : undefined,
      });
      setProducts((current) => current.map((p) => (p.id === product.id ? updated : p)));
      setDraftDescriptions((drafts) => {
        const next = { ...drafts };
        delete next[product.id];
        return next;
      });
    } catch {
      setDraftErrors((errors) => ({
        ...errors,
        [product.id]: "Something went wrong while saving the description. Please try again.",
      }));
    } finally {
      setAcceptingIds((ids) => {
        const next = new Set(ids);
        next.delete(product.id);
        return next;
      });
    }
  }

  return (
    <div className="flex flex-col gap-4 border-t border-border pt-6">
      <h2 className="text-lg font-semibold">Products</h2>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3" noValidate>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="product-title">Title</Label>
          <Input
            id="product-title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            aria-invalid={titleError ? true : undefined}
            disabled={isSubmitting}
          />
          {titleError && (
            <p role="alert" className="text-sm text-destructive">
              {titleError}
            </p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="product-subtitle">Subtitle</Label>
          <Input
            id="product-subtitle"
            value={subtitle}
            onChange={(event) => setSubtitle(event.target.value)}
            disabled={isSubmitting}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="product-description">Description</Label>
          <Input
            id="product-description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            disabled={isSubmitting}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="product-category">Category</Label>
          <Input
            id="product-category"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            disabled={isSubmitting}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="product-tags">Tags (comma-separated)</Label>
          <Input
            id="product-tags"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            disabled={isSubmitting}
          />
        </div>

        <div className="flex gap-3">
          <div className="flex flex-1 flex-col gap-1.5">
            <Label htmlFor="product-price-amount">Price</Label>
            <Input
              id="product-price-amount"
              inputMode="decimal"
              value={priceAmount}
              onChange={(event) => setPriceAmount(event.target.value)}
              disabled={isSubmitting}
            />
          </div>
          <div className="flex w-24 flex-col gap-1.5">
            <Label htmlFor="product-price-currency">Currency</Label>
            <Input
              id="product-price-currency"
              value={priceCurrency}
              onChange={(event) => setPriceCurrency(event.target.value.toUpperCase())}
              disabled={isSubmitting}
              maxLength={3}
            />
          </div>
        </div>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Add Product"}
        </Button>

        {submitError && (
          <p role="alert" className="text-sm text-destructive">
            {submitError}
          </p>
        )}
      </form>

      {isLoading && <p className="text-sm text-muted-foreground">Loading products...</p>}

      {loadError && (
        <p role="alert" className="text-sm text-destructive">
          {loadError}
        </p>
      )}

      {!isLoading && !loadError && products.length === 0 && (
        <p className="text-sm text-muted-foreground">No products yet. Add one above.</p>
      )}

      {products.length > 0 && (
        <ul className="flex flex-col gap-3">
          {products.map((product) => {
            const isPending = pendingActionIds.has(product.id);
            const actionError = actionErrors[product.id];
            const isGenerating = generatingIds.has(product.id);
            const isAccepting = acceptingIds.has(product.id);
            const draftDescription = draftDescriptions[product.id];
            const draftError = draftErrors[product.id];

            return (
              <li
                key={product.id}
                className="flex flex-col gap-2 rounded-lg border border-border px-3 py-2 text-sm"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{product.title}</span>
                  <span className="text-muted-foreground">{STATUS_LABELS[product.status]}</span>
                </div>

                {product.subtitle && <p className="text-muted-foreground">{product.subtitle}</p>}

                {product.pricing && (
                  <p>
                    {product.pricing.amount} {product.pricing.currency}
                  </p>
                )}

                {product.tags.length > 0 && (
                  <p className="text-muted-foreground">{product.tags.join(", ")}</p>
                )}

                <div>
                  <p className="font-medium">Description</p>
                  <p className="text-muted-foreground">
                    {product.description || "No description yet."}
                  </p>
                </div>

                {actionError && (
                  <p role="alert" className="text-sm text-destructive">
                    {actionError}
                  </p>
                )}

                <div className="flex gap-2">
                  {product.status === "draft" && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      disabled={isPending}
                      onClick={() => void handleMarkReady(product.id)}
                    >
                      Mark Ready for Publishing
                    </Button>
                  )}
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={isPending}
                    onClick={() => void handleDelete(product.id)}
                  >
                    Delete
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={isGenerating}
                    onClick={() => void handleGenerateDescription(product.id)}
                  >
                    {isGenerating ? "Generating..." : "Generate Description"}
                  </Button>
                </div>

                {draftError && (
                  <p role="alert" className="text-sm text-destructive">
                    {draftError}
                  </p>
                )}

                {draftDescription !== undefined && (
                  <div className="flex flex-col gap-2 rounded-lg border border-border bg-muted/30 p-3">
                    <p className="font-medium">Generated description (draft)</p>
                    <p className="text-muted-foreground">{draftDescription}</p>
                    <div className="flex gap-2">
                      <Button
                        type="button"
                        size="sm"
                        disabled={isAccepting}
                        onClick={() => void handleAcceptDescription(product)}
                      >
                        {isAccepting ? "Saving..." : "Accept"}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        disabled={isAccepting}
                        onClick={() => handleDiscardDescription(product.id)}
                      >
                        Discard
                      </Button>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
