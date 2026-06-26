# RAG Studio Pro frontend — Next.js dev container.
# Production multi-stage build is added in the deployment phase.
FROM node:22-alpine

RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

WORKDIR /app

# Install dependencies first for layer caching.
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install

COPY . .

EXPOSE 3000

CMD ["pnpm", "dev"]
