"""
Rule-based modesty classifier — no API calls, no cost.

Filters based on product name keywords since we're already scraping
skirts-specific category pages. Items with mini/micro/short/skort in
the name are rejected; everything else in a skirts category is accepted.
"""

REJECT_KEYWORDS = [
    "mini", "micro", "skort", "romper", "playsuit",
    "above the knee", "above-the-knee", "short skirt",
    "cutout", "cut-out", "high slit",
]

MIDI_KEYWORDS = ["midi", "mid-length", "mid length", "below the knee", "below-the-knee"]
MAXI_KEYWORDS = ["maxi", "long", "floor-length", "floor length", "ankle", "full-length"]
KNEE_KEYWORDS = ["knee", "knee-length", "knee length"]

def classify_product_by_name(name: str) -> dict:
    """
    Classify a product by name alone.
    Returns is_modest, length, confidence, reason.
    """
    name_lower = name.lower()

    # Hard reject
    for kw in REJECT_KEYWORDS:
        if kw in name_lower:
            return {
                "is_modest": False,
                "confidence": 0.9,
                "reason": f'Rejected: contains "{kw}"',
                "length": "mini",
                "item_type": "skirt",
                "has_sleeve_issue": False,
            }

    # Determine length from name
    length = "unknown"
    for kw in MIDI_KEYWORDS:
        if kw in name_lower:
            length = "midi"
            break
    if length == "unknown":
        for kw in MAXI_KEYWORDS:
            if kw in name_lower:
                length = "maxi"
                break
    if length == "unknown":
        for kw in KNEE_KEYWORDS:
            if kw in name_lower:
                length = "knee"
                break

    return {
        "is_modest": True,
        "confidence": 0.85 if length != "unknown" else 0.6,
        "reason": f"Skirts category, length={length}, no red-flag keywords",
        "length": length,
        "item_type": "skirt",
        "has_sleeve_issue": False,
    }


# Keep async signature so run.py doesn't need changes
async def classify_product(image_url: str, product_name: str = "") -> dict:
    return classify_product_by_name(product_name)
