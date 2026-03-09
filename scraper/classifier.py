"""
Claude vision classifier for modest clothing detection.
Analyzes product images against modesty criteria:
  - Skirt/dress only (no pants)
  - Knee-length or longer
  - Sleeves past shoulders (for dresses/full outfits)
  - No midriff/belly visible
"""

import json
import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a fashion classifier for a modest clothing aggregator.
You analyze product images and determine if items meet specific modesty criteria.
Always respond with valid JSON only — no markdown, no explanation outside the JSON."""

CLASSIFICATION_PROMPT = """Analyze this clothing product image for modesty criteria.

Criteria to check:
1. ITEM TYPE: Must be a skirt or dress (not pants, shorts, jeans, or trousers)
2. LENGTH: Hemline must reach at or below the knee (knee/midi/maxi length)
3. COVERAGE: No belly or midriff visible in the photo
4. SLEEVES: If the item is a dress or a full outfit is shown, sleeves must extend past the shoulder (no sleeveless, strapless, or off-shoulder styles)

Product name hint: {product_name}

Respond with this exact JSON format:
{{
  "is_modest": true or false,
  "confidence": 0.0 to 1.0,
  "reason": "one sentence explanation of pass or fail",
  "length": "mini" or "knee" or "midi" or "maxi" or "unknown",
  "item_type": "skirt" or "dress" or "pants" or "other" or "unknown",
  "has_sleeve_issue": true or false
}}"""


async def classify_product(image_url: str, product_name: str = "") -> dict:
    """
    Classify a product image for modesty.
    Returns a dict with is_modest, confidence, reason, length, item_type.
    """
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "url",
                                "url": image_url,
                            },
                        },
                        {
                            "type": "text",
                            "text": CLASSIFICATION_PROMPT.format(
                                product_name=product_name or "Unknown"
                            ),
                        },
                    ],
                }
            ],
        )

        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text)
        return result

    except json.JSONDecodeError:
        return {
            "is_modest": False,
            "confidence": 0.0,
            "reason": "Classification failed: could not parse response",
            "length": "unknown",
            "item_type": "unknown",
            "has_sleeve_issue": False,
        }
    except Exception as e:
        return {
            "is_modest": False,
            "confidence": 0.0,
            "reason": f"Classification error: {str(e)[:100]}",
            "length": "unknown",
            "item_type": "unknown",
            "has_sleeve_issue": False,
        }
