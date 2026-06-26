export interface Role {
  id: string;
  name: string;
  permissions: string[];
}

export interface User {
  id: string;
  clerk_user_id: string;
  organization_id: string;
  email: string;
  full_name: string | null;
  role: Role;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
  created_at: string;
}

export interface Workspace {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  created_at: string;
}
