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

export type ProductIntelligenceStatus = "draft" | "ready_for_publishing" | "published";

export interface Specification {
  name: string;
  value: string;
}

export interface SeoMetadata {
  meta_title: string | null;
  meta_description: string | null;
  slug: string | null;
}

export interface Pricing {
  amount: string;
  currency: string;
  compare_at_amount: string | null;
}

export interface ImageAsset {
  url: string;
  alt_text: string | null;
}

export interface PublishingMetadata {
  published_channels: string[];
  published_at: string | null;
}

export interface ProductIntelligence {
  id: string;
  project_id: string;
  research_session_id: string | null;
  title: string;
  subtitle: string | null;
  description: string | null;
  features: string[];
  specifications: Specification[];
  category: string | null;
  tags: string[];
  keywords: string[];
  seo: SeoMetadata;
  pricing: Pricing | null;
  images: ImageAsset[];
  publishing: PublishingMetadata;
  status: ProductIntelligenceStatus;
  created_at: string;
  updated_at: string;
}
