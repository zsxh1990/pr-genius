"""prgenius — Evidence-backed lookup for big-repo PR contributions.

Local-only. Zero runtime ops. Stdlib-only (PyYAML opt-in via extras).

Public surface:
- load()       — parse one markdown file into a dict (frontmatter + body)
- iter_profiles(repo_root) — yield Repo Profile dicts
- iter_case_studies(repo_root) — yield PR Case Study dicts
- profile_get(repo_root, "<org>/<repo>") — look up a single profile
- schema_info() — return supported OKF schema versions
"""

__version__ = "0.7.7"
__all__ = [
    "__version__",
    "load",
    "iter_profiles",
    "iter_case_studies",
    "profile_get",
    "schema_info",
]
