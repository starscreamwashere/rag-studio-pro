"""RBAC permissions and the default role definitions.

These four roles are seeded by the initial Alembic migration. Permission
strings are coarse-grained capabilities checked by API dependencies.
"""

# Capability constants (extended in later phases as features land).
CREATE_KNOWLEDGE_BASE = "knowledge_base:create"
UPLOAD_DOCUMENTS = "documents:upload"
RUN_EXPERIMENTS = "experiments:run"
VIEW_ANALYTICS = "analytics:view"
MANAGE_USERS = "users:manage"
ADMIN_ACTIONS = "admin:actions"

VIEWER_PERMISSIONS = [VIEW_ANALYTICS]
ANALYST_PERMISSIONS = [
    *VIEWER_PERMISSIONS,
    CREATE_KNOWLEDGE_BASE,
    UPLOAD_DOCUMENTS,
    RUN_EXPERIMENTS,
]
ORG_ADMIN_PERMISSIONS = [*ANALYST_PERMISSIONS, MANAGE_USERS]
SUPER_ADMIN_PERMISSIONS = [*ORG_ADMIN_PERMISSIONS, ADMIN_ACTIONS]

# Canonical role names.
ROLE_SUPER_ADMIN = "Super Admin"
ROLE_ORG_ADMIN = "Organization Admin"
ROLE_ANALYST = "Analyst"
ROLE_VIEWER = "Viewer"

DEFAULT_ROLES: dict[str, list[str]] = {
    ROLE_SUPER_ADMIN: SUPER_ADMIN_PERMISSIONS,
    ROLE_ORG_ADMIN: ORG_ADMIN_PERMISSIONS,
    ROLE_ANALYST: ANALYST_PERMISSIONS,
    ROLE_VIEWER: VIEWER_PERMISSIONS,
}
