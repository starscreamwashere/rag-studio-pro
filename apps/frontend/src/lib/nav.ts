import {
  LayoutDashboard,
  Database,
  Upload,
  FlaskConical,
  MessageSquare,
  BarChart3,
  ShieldCheck,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  /** Phase that ships this destination's real functionality. */
  phase: number;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, phase: 1 },
  { label: "Knowledge Bases", href: "/knowledge-bases", icon: Database, phase: 2 },
  { label: "Ingestion", href: "/ingestion", icon: Upload, phase: 2 },
  { label: "Studio", href: "/studio", icon: FlaskConical, phase: 6 },
  { label: "Chat Assistant", href: "/chat", icon: MessageSquare, phase: 4 },
  { label: "Analytics", href: "/analytics", icon: BarChart3, phase: 6 },
  { label: "Admin", href: "/admin", icon: ShieldCheck, phase: 1 },
  { label: "Settings", href: "/settings", icon: Settings, phase: 1 },
];
