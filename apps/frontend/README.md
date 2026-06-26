# RAG Studio Pro — Frontend

Next.js (App Router) + TypeScript + Tailwind CSS v4 + shadcn/ui.

## Run via Docker (recommended)

From the repo root:

```bash
docker compose up frontend
```

## Run locally

```bash
pnpm install
cp .env.local.example .env.local
pnpm dev
```

App: http://localhost:3000

## Design system

Tokens from the UI/UX Design Brief ("Warm Minimal Intelligence") live as CSS
variables in `src/app/globals.css` and are mapped into Tailwind via `@theme`.
Add shadcn/ui components with:

```bash
pnpm dlx shadcn@latest add button card badge
```

## Layout

```
src/
  app/            App Router (layout, pages, globals.css)
  components/     Shared components (ui/ holds shadcn primitives)
  lib/utils.ts    cn() class helper
```
