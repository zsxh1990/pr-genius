
def compute_dco_signal(body: str) -> dict:
    """Check if PR body mentions DCO sign-off."""
    if "signed-off-by" in body.lower():
        return {"key": "dco_mentioned", "description": "DCO sign-off mentioned in PR body"}
    return {"key": "dco_missing", "description": "DCO sign-off not mentioned"}
