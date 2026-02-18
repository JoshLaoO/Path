from schemas import PlanCreate, PlanDayCreate


# Placeholder verse pool: theme -> list of verse strings (reference + text).
# Used to assign a verse to each plan day; cycles if duration_days > len(verses).
VERSE_POOL: dict[str, list[str]] = {
    "default": [
        "Psalm 23:1 - The Lord is my shepherd; I shall not want.",
        "Proverbs 3:5-6 - Trust in the Lord with all your heart.",
        "Isaiah 41:10 - Fear not, for I am with you.",
        "Philippians 4:13 - I can do all things through Christ who strengthens me.",
        "Matthew 11:28 - Come to me, all who labor and are heavy laden.",
        "Romans 8:28 - And we know that for those who love God all things work together for good.",
        "Joshua 1:9 - Be strong and courageous. Do not be frightened.",
        "Psalm 46:10 - Be still, and know that I am God.",
    ],
    "peace": [
        "John 14:27 - Peace I leave with you; my peace I give to you.",
        "Philippians 4:7 - And the peace of God, which surpasses all understanding.",
        "Isaiah 26:3 - You keep him in perfect peace whose mind is stayed on you.",
    ],
    "strength": [
        "Isaiah 40:31 - They who wait for the Lord shall renew their strength.",
        "2 Corinthians 12:9 - My grace is sufficient for you.",
        "Psalm 18:32 - It is God who arms me with strength.",
    ],
}


def get_verses_for_theme(theme: str) -> list[str]:
    """Return the verse list for the given theme, or default pool."""
    key = theme.lower().strip() if theme else "default"
    return VERSE_POOL.get(key, VERSE_POOL["default"])


def generate_plan(
    user_id: int, title: str, description: str | None = None
) -> PlanCreate:
    """Generate a plan with the given user_id, title and optional description."""
    return PlanCreate(user_id=user_id, title=title, description=description or "")


def generate_plan_days(
    plan_id: int, theme: str, duration_days: int
) -> list[PlanDayCreate]:
    """
    Generate PlanDay create payloads for the given plan_id, assigning verses
    from the pool for the theme. Cycles through the verse list if duration_days
    exceeds the pool size.
    """
    verses = get_verses_for_theme(theme)
    return [
        PlanDayCreate(
            plan_id=plan_id,
            day_number=day_num,
            verse=verses[(day_num - 1) % len(verses)],
        )
        for day_num in range(1, duration_days + 1)
    ]
