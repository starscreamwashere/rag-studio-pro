"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";
import { cn } from "@/lib/utils";
import { NAV_ITEMS } from "@/lib/nav";
import { WorkspaceSwitcher } from "@/components/app/workspace-switcher";
import type { User } from "@/lib/types";

export function Sidebar({ user }: { user: User }) {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-[280px] flex-col border-r bg-surface-1">
      <div className="px-5 py-5">
        <span className="font-semibold tracking-tight">RAG Studio Pro</span>
      </div>

      <div className="px-3">
        <WorkspaceSwitcher />
      </div>

      <nav className="mt-4 flex flex-1 flex-col gap-1 px-3">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-[var(--radius-button)] px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-primary/10 font-medium text-primary"
                  : "text-muted-foreground hover:bg-surface-2 hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="flex items-center gap-3 border-t px-5 py-4">
        <UserButton />
        <div className="min-w-0">
          <p className="truncate text-sm font-medium">{user.full_name ?? user.email}</p>
          <p className="truncate text-xs text-muted-foreground">{user.role.name}</p>
        </div>
      </div>
    </aside>
  );
}
