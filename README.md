# Project Alpha — Alpha Research Platform (ARP)

Production-grade SaaS monorepo. Clean Architecture, SOLID, feature-first, modular monorepo.

## Stack

- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL (Supabase) — not yet connected
- **Tooling**: pnpm workspaces + Turborepo

## Structure

```
apps/
  web/            Next.js frontend
  api/            FastAPI backend
packages/
  ui/             Shared React component library (shadcn/ui based)
  config/         Shared TypeScript + ESLint configuration
  types/          Shared TypeScript types
  utils/          Shared framework-agnostic utilities
infrastructure/
  supabase/       Supabase config (migrations, seed) — empty scaffold
  docker/         Container definitions — empty scaffold
docs/             Architecture and product docs
```

## Requirements

- Node.js >= 20
- pnpm (via Corepack: `corepack enable pnpm`)
- Python 3.12 (`brew install python@3.12`)

## Setup

```bash
pnpm install

cd apps/api
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Development

```bash
pnpm dev          # run all apps in parallel (via Turborepo)
pnpm dev:web      # run only the Next.js app
pnpm dev:api      # run only the FastAPI app
```

## Other scripts

```bash
pnpm build        # build all apps
pnpm lint         # lint all apps/packages
pnpm type-check   # type-check all TypeScript apps/packages
pnpm test         # run tests across the monorepo
pnpm clean        # remove build artifacts and node_modules
```
