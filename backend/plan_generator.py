from schemas import PlanCreate


def generate_plan(title: str, description: str | None = None) -> PlanCreate:
    """Generate a plan with the given title and optional description."""
    return PlanCreate(title=title, description=description or "")
