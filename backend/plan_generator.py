from bible_api import fetch_verse
from schemas import PlanCreate, PlanDayCreate


# Theme -> list of Bible references (e.g. "John 3:16"). Text is fetched from bible-api.com.
# Theme key is lowercased; add variants like "defending faith" if you want multiple phrases to match.
REFERENCE_POOL: dict[str, list[str]] = {
    "default": [
        "Psalm 23:1",
        "Proverbs 3:5-6",
        "Isaiah 41:10",
        "Philippians 4:13",
        "Matthew 11:28",
        "Romans 8:28",
        "Joshua 1:9",
        "Psalm 46:10",
    ],
    "peace": [
        "John 14:27",
        "Philippians 4:7",
        "Isaiah 26:3",
    ],
    "strength": [
        "Isaiah 40:31",
        "2 Corinthians 12:9",
        "Psalm 18:32",
    ],
    "defending your faith": [
        "1 Peter 3:15",
        "Jude 1:3",
        "2 Corinthians 10:4-5",
        "Colossians 4:6",
        "2 Timothy 2:15",
        "Titus 1:9",
        "Acts 17:11",
    ],
    "comfort": [
        "Psalm 34:18",
        "Matthew 5:4",
        "2 Corinthians 1:3-4",
        "Revelation 21:4",
        "Psalm 147:3",
    ],
    "grief": [
        "Psalm 34:18",
        "Matthew 5:4",
        "2 Corinthians 1:3-4",
        "Revelation 21:4",
        "Psalm 147:3",
    ],
    "fear": [
        "Isaiah 41:10",
        "Psalm 56:3",
        "Philippians 4:6-7",
        "2 Timothy 1:7",
        "Matthew 6:34",
    ],
    "anxiety": [
        "Isaiah 41:10",
        "Psalm 56:3",
        "Philippians 4:6-7",
        "2 Timothy 1:7",
        "Matthew 6:34",
    ],
    "hope": [
        "Romans 15:13",
        "Jeremiah 29:11",
        "Hebrews 6:19",
        "Psalm 42:11",
        "Lamentations 3:22-23",
    ],
    "gratitude": [
        "1 Thessalonians 5:18",
        "Psalm 100:4-5",
        "Colossians 3:15-17",
        "Psalm 107:1",
    ],
    "thankfulness": [
        "1 Thessalonians 5:18",
        "Psalm 100:4-5",
        "Colossians 3:15-17",
        "Psalm 107:1",
    ],
    "love": [
        "1 John 4:8",
        "John 13:34-35",
        "1 Corinthians 13:4-7",
        "Romans 8:38-39",
    ],
    "wisdom": [
        "Proverbs 3:5-6",
        "James 1:5",
        "Proverbs 2:6",
        "Colossians 2:3",
        "Proverbs 9:10",
    ],
    "patience": [
        "Psalm 27:14",
        "James 1:4",
        "Isaiah 40:31",
        "Galatians 5:22",
        "Romans 12:12",
    ],
    "waiting": [
        "Psalm 27:14",
        "James 1:4",
        "Isaiah 40:31",
        "Galatians 5:22",
        "Romans 12:12",
    ],
    "forgiveness": [
        "Ephesians 4:32",
        "Colossians 1:13-14",
        "Matthew 6:14-15",
        "1 John 1:9",
    ],
    "identity": [
        "2 Corinthians 5:17",
        "Galatians 2:20",
        "Romans 8:1",
        "1 Peter 2:9",
        "Ephesians 2:10",
    ],
    "identity in christ": [
        "2 Corinthians 5:17",
        "Galatians 2:20",
        "Romans 8:1",
        "1 Peter 2:9",
        "Ephesians 2:10",
    ],
    "prayer": [
        "Matthew 6:9-13",
        "1 Thessalonians 5:17",
        "Philippians 4:6",
        "James 5:16",
        "Luke 11:9",
    ],
    "serving": [
        "Philippians 2:3-4",
        "Mark 10:45",
        "Galatians 5:13",
        "John 13:14-15",
    ],
    "humility": [
        "Philippians 2:3-4",
        "Mark 10:45",
        "Galatians 5:13",
        "John 13:14-15",
    ],
    "faith": [
        "Hebrews 11:1",
        "Romans 10:17",
        "Mark 9:23",
        "Proverbs 3:5",
        "Hebrews 11:6",
    ],
    "trust": [
        "Hebrews 11:1",
        "Romans 10:17",
        "Proverbs 3:5",
        "Hebrews 11:6",
        "Psalm 56:3",
    ],
    "rest": [
        "Matthew 11:28-30",
        "Exodus 20:8-10",
        "Psalm 23:2-3",
        "Hebrews 4:9-10",
    ],
    "sabbath": [
        "Matthew 11:28-30",
        "Exodus 20:8-10",
        "Psalm 23:2-3",
        "Hebrews 4:9-10",
    ],
    "courage": [
        "Joshua 1:9",
        "Acts 4:31",
        "2 Timothy 1:7",
        "Ephesians 6:10",
        "Psalm 31:24",
    ],
    "boldness": [
        "Joshua 1:9",
        "Acts 4:31",
        "2 Timothy 1:7",
        "Ephesians 6:10",
        "Psalm 31:24",
    ],
    "new beginnings": [
        "Lamentations 3:22-23",
        "Isaiah 43:18-19",
        "2 Corinthians 5:17",
        "Psalm 51:10",
    ],
    "renewal": [
        "Lamentations 3:22-23",
        "Isaiah 43:18-19",
        "2 Corinthians 5:17",
        "Psalm 51:10",
    ],
}


def get_references_for_theme(theme: str) -> list[str]:
    """Return the reference list for the given theme, or default pool."""
    key = theme.lower().strip() if theme else "default"
    return REFERENCE_POOL.get(key, REFERENCE_POOL["default"]).copy()


def generate_plan(
    user_id: int, title: str, description: str | None = None
) -> PlanCreate:
    """Generate a plan with the given user_id, title and optional description."""
    return PlanCreate(user_id=user_id, title=title, description=description or "")


def generate_plan_days(
    plan_id: int,
    theme: str,
    duration_days: int,
    translation: str = "web",
) -> list[PlanDayCreate]:
    """
    Generate PlanDay create payloads with verse text from bible-api.com.
    Uses theme to pick references, fetches real verse text for each day.
    """
    references = get_references_for_theme(theme)
    out: list[PlanDayCreate] = []
    for day_num in range(1, duration_days + 1):
        ref = references[(day_num - 1) % len(references)]
        verse_text = fetch_verse(ref, translation=translation)
        out.append(
            PlanDayCreate(
                plan_id=plan_id,
                day_number=day_num,
                verse=verse_text,
                passage_reference=ref,
                key_verse=None,
            )
        )
    return out
