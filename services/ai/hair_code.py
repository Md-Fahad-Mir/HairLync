

import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")  # Default: GPT-5.5 for best vision
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_MAX_RESULTS = max(1, int(os.getenv("YOUTUBE_MAX_RESULTS", "3")))
YOUTUBE_SAFE_SEARCH = os.getenv("YOUTUBE_SAFE_SEARCH", "moderate")
YOUTUBE_TIMEOUT = float(os.getenv("YOUTUBE_TIMEOUT", "10"))


def _has_usable_youtube_key() -> bool:
    if not YOUTUBE_API_KEY:
        return False
    key = YOUTUBE_API_KEY.strip()
    if not key or key.startswith("http://") or key.startswith("https://"):
        return False
    return True

# Model Priority List (will use first available):
# GPT-5.5 is best for deep image understanding and contextual reasoning
PREFERRED_MODELS = [
    "gpt-5.5",                  # Best: Deep vision + context analysis
    "gpt-5",                    # Future: GPT-5 base
    "gpt-5-preview",            # Future: GPT-5 preview
    "chatgpt-4o-latest",        # Good: Latest ChatGPT-4o
    "o1-preview",               # Good: Advanced reasoning
    "gpt-4o",                   # Stable: GPT-4o
    "gpt-4o-mini",              # Budget: Fast and cheap
]

OUTPUT_DIR = Path("./reports")


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT  (analysis + recommendations together)
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert AI consultant in facial aesthetics, dermatology,
trichology, hairstyling, and color theory. Analyze the photo deeply and honestly,
based only on visible features (no race/ethnicity assumptions).
Return ONE valid JSON object — no prose, no markdown, no code fences.
All scores are integers 0-100. If unobservable, use "unknown" / null / [] / false."""


SCHEMA = """
{
  "face_shape_analysis": {
    "detected_shape": "oval|round|square|rectangle|heart|diamond|triangle|oblong",
    "confidence_score": 0-100,
    "reasoning": "...",
    "facial_symmetry": {"score": 0-100, "notes": "..."},
    "jawline": "...", "cheekbones": "...", "chin_structure": "...",
    "forehead_proportions": "...", "facial_geometry_notes": "...",
    "golden_ratio_alignment": {"score": 0-100, "notes": "..."},
    "facial_architecture_summary": "..."
  },
  "skin_analysis": {
    "skin_tone": "...", "undertone": "warm|cool|neutral|olive",
    "texture": "...", "condition": "dry|oily|combination|normal",
    "acne_observation": "...", "dark_circles": "...", "redness": "...",
    "wrinkles": "...", "pores": "...",
    "smoothness_score": 0-100, "overall_skin_health_score": 0-100,
    "notes": "..."
  },
  "beard_analysis": {
    "has_beard": true_or_false,
    "style": "clean_shave|stubble|short_beard|full_beard|goatee|long_beard|other",
    "density": "...", "length": "...", "grooming_condition": "...", "notes": "..."
  },
  "hair_analysis": {
    "current_hairstyle": "...", "length_observed": "...",
    "texture_classification": "straight|wavy|curly|coily",
    "pattern": "...", "density": "low|medium|high",
    "thickness": "fine|medium|thick", "volume": "...",
    "hairline_condition": "...", "curl_pattern": "...",
    "growth_direction": "...", "shine_level": "low|medium|high",
    "frizz_level": "low|medium|high", "hair_health_score": 0-100,
    "damage_observation": "...", "thinning_observation": "...",
    "split_ends": "...", "dry_or_oily": "...", "scalp_visibility": "...",
    "notes": "..."
  },
  "hair_color_analysis": {
    "current_color": "...", "tone": "...", "warm_cool_balance": "...",
    "estimated_natural_color": "...", "color_depth": "..."
  },
  "style_trend_analysis": {
    "current_classification": "modern|trendy|classic|outdated",
    "trend_score": 0-100, "celebrity_inspired_category": "...", "notes": "..."
  },
  "recommendations": {
    "hairstyles": [
      {
        "name": "...", "description": "...", "why_it_suits": "...",
        "compatibility_score": 0-100,
        "styling_difficulty": "easy|moderate|hard",
        "maintenance_level": "low|medium|high",
        "styling_tips": ["...", "...", "..."],
        "suitability": "casual|professional|both"
      }
    ],
    "hair_colors": {
      "best_matching": ["..."], "natural_options": ["..."],
      "bold_options": ["..."], "colors_to_avoid": ["..."],
      "reasoning": "..."
    },
    "beard_recommendations": [
      {"style": "...", "why_it_suits": "...", "compatibility_score": 0-100}
    ],
    "hair_care": {
      "growth_suggestions": ["..."], "repair_suggestions": ["..."],
      "hair_fall_prevention": ["..."], "scalp_care": ["..."],
      "home_remedies": ["..."], "maintenance_routine": ["..."],
      "product_recommendations": {
        "oils": ["..."], "shampoo": ["..."], "conditioner": ["..."],
        "serum": ["..."], "hair_masks": ["..."]
      }
    },
    "face_care": {
      "skin_care_advice": ["..."], "acne_prevention": ["..."],
      "hydration": ["..."], "texture_improvement": ["..."],
      "grooming_advice": ["..."]
    }
  },
  "summary": "3-5 sentence overall summary."
}
""".strip()


def build_user_prompt(gender: str, hair_length: str) -> str:
    return (
        f"User input — Gender: {gender}, Hair length: {hair_length}.\n"
        f"Treat HAIR analysis as highest priority and recommend AT LEAST 3 hairstyles "
        f"tailored to face shape, hair texture, density, skin tone & undertone, "
        f"using golden-ratio principles and color harmony.\n\n"
        f"Return ONLY this JSON schema:\n{SCHEMA}"
    )


def build_tutorial_query(topic: str, gender: str = "", hair_length: str = "") -> str:
    parts = [topic.strip(), "tutorial"]
    if gender.strip():
        parts.append(gender.strip())
    if hair_length.strip():
        parts.append(hair_length.strip())
    return " ".join(part for part in parts if part)


def _youtube_search_url(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def fetch_youtube_tutorials(query: str, max_results: int | None = None) -> list[dict]:
    query = query.strip()
    if not query:
        return []

    fallback = [
        {
            "title": f'Search YouTube for "{query}"',
            "url": _youtube_search_url(query),
            "source": "youtube_search",
        }
    ]

    if not _has_usable_youtube_key():
        return fallback

    limit = max_results or YOUTUBE_MAX_RESULTS
    params = {
        "part": "snippet",
        "type": "video",
        "order": "relevance",
        "maxResults": str(limit),
        "q": query,
        "safeSearch": YOUTUBE_SAFE_SEARCH,
        "key": YOUTUBE_API_KEY,
    }
    url = "https://www.googleapis.com/youtube/v3/search?" + urlencode(params)

    try:
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=YOUTUBE_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return fallback

    tutorials: list[dict] = []
    for item in payload.get("items") or []:
        snippet = item.get("snippet") or {}
        video_id = (item.get("id") or {}).get("videoId")
        if not video_id:
            continue

        thumbnails = snippet.get("thumbnails") or {}
        tutorials.append(
            {
                "title": snippet.get("title") or query,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "video_id": video_id,
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "description": snippet.get("description"),
                "thumbnail_url": (thumbnails.get("medium") or thumbnails.get("default") or {}).get("url"),
                "source": "youtube_api",
            }
        )

    return tutorials or fallback


def enrich_analysis_with_tutorials(data: dict) -> dict:
    recommendations = data.get("recommendations") or {}
    if not isinstance(recommendations, dict):
        return data

    meta = data.get("_meta") or {}
    gender = str(meta.get("gender") or "").strip()
    hair_length = str(meta.get("hair_length") or "").strip()
    hair_analysis = data.get("hair_analysis") or {}
    texture = str(hair_analysis.get("texture_classification") or "").strip()
    density = str(hair_analysis.get("density") or "").strip()

    for hairstyle in recommendations.get("hairstyles") or []:
        if not isinstance(hairstyle, dict):
            continue
        style_name = str(hairstyle.get("name") or "").strip()
        if not style_name:
            continue
        query = build_tutorial_query(f"{style_name} hairstyle", gender, hair_length)
        hairstyle["tutorials"] = fetch_youtube_tutorials(query)

    hair_care = recommendations.get("hair_care")
    if isinstance(hair_care, dict):
        care_bits = [part for part in [texture, density, gender, hair_length] if part]
        if care_bits:
            query = build_tutorial_query(f"hair care for {' '.join(care_bits)}")
            hair_care["tutorials"] = fetch_youtube_tutorials(query)

    for beard in recommendations.get("beard_recommendations") or []:
        if not isinstance(beard, dict):
            continue
        beard_style = str(beard.get("style") or "").strip()
        if not beard_style:
            continue
        query = build_tutorial_query(f"{beard_style} beard", gender, hair_length)
        beard["tutorials"] = fetch_youtube_tutorials(query)

    return data


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
def encode_image(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower().lstrip(".")
    if ext == "jpg":
        ext = "jpeg"
    if ext not in {"jpeg", "png", "webp", "gif"}:
        raise ValueError(f"Unsupported image format: .{ext}")
    return base64.b64encode(path.read_bytes()).decode("utf-8"), f"image/{ext}"


def get_best_available_model(client: OpenAI, preferred_model: str) -> str:
    """
    Check if the preferred model is available, otherwise find the best alternative.
    Returns the model name to use.
    """
    try:
        # Try to list available models
        models = client.models.list()
        available_model_ids = [model.id for model in models.data]
        
        # Check if preferred model is available
        if preferred_model in available_model_ids:
            return preferred_model
        
        # Check for GPT-5 or newer models
        for model_name in PREFERRED_MODELS:
            if model_name in available_model_ids:
                print(f"ℹ️  Using {model_name} (better than configured model)")
                return model_name
        
        # Fallback to configured model (API will error if not available)
        return preferred_model
        
    except Exception:
        # If we can't list models, just use the configured one
        return preferred_model


def analyze(image_path: Path, gender: str, hair_length: str) -> dict:
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set in environment.")
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    client = OpenAI(api_key=API_KEY)
    
    # Automatically select the best available model
    model_to_use = get_best_available_model(client, MODEL)
    
    b64, media_type = encode_image(image_path)

    # Prepare API parameters based on model capabilities
    api_params = {
        "model": model_to_use,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": build_user_prompt(gender, hair_length)},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{b64}",
                            "detail": "high",  # Use "high" for best quality analysis
                        },
                    },
                ],
            },
        ],
        "response_format": {"type": "json_object"},
    }
    
    # GPT-5.5 uses max_completion_tokens and doesn't support custom temperature
    if "gpt-5" in model_to_use.lower():
        api_params["max_completion_tokens"] = 4096
        # GPT-5.5 only supports temperature=1 (default), so we don't set it
    else:
        # Older models use max_tokens and support custom temperature
        api_params["max_tokens"] = 4096
        api_params["temperature"] = 0.3
    
    response = client.chat.completions.create(**api_params)

    content = response.choices[0].message.content or ""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Model returned invalid JSON: {e}\nRaw: {content[:500]}")

    data["_meta"] = {
        "model": model_to_use,  # Store actual model used
        "configured_model": MODEL,
        "image_path": str(image_path),
        "gender": gender,
        "hair_length": hair_length,
        "tokens_used": response.usage.total_tokens if response.usage else None,
    }
    return data


# ─────────────────────────────────────────────────────────────────────────────
# REPORT  (Markdown)
# ─────────────────────────────────────────────────────────────────────────────
def s(v, default="—"):
    """Safe value getter."""
    return default if v is None or v == "" else v


def _bullets(items):
    return "\n".join(f"- {x}" for x in (items or []))


def to_markdown(data: dict) -> str:
    out: list[str] = []
    meta = data.get("_meta", {})

    out.append("# Face & Hair AI Analysis Report")
    out.append(f"\n_Generated: {datetime.now():%Y-%m-%d %H:%M:%S}_\n")
    out.append(f"**Image:** `{s(meta.get('image_path'))}`  ")
    out.append(f"**Gender:** {s(meta.get('gender'))}  |  "
               f"**Hair length:** {s(meta.get('hair_length'))}  ")
    out.append(f"**Model:** `{s(meta.get('model'))}`\n")

    if data.get("summary"):
        out.append("## Summary\n" + data["summary"] + "\n")

    # ---- Face shape
    fs = data.get("face_shape_analysis", {}) or {}
    sym = fs.get("facial_symmetry", {}) or {}
    gr = fs.get("golden_ratio_alignment", {}) or {}
    out.append("## Face Shape Analysis")
    out.append(f"- **Detected shape:** **{s(fs.get('detected_shape'))}** "
               f"({s(fs.get('confidence_score'))}/100)")
    out.append(f"- **Reasoning:** {s(fs.get('reasoning'))}")
    out.append(f"- **Symmetry:** {s(sym.get('score'))}/100 — {s(sym.get('notes'))}")
    out.append(f"- **Golden ratio:** {s(gr.get('score'))}/100 — {s(gr.get('notes'))}")
    for label, key in [
        ("Jawline", "jawline"), ("Cheekbones", "cheekbones"),
        ("Chin", "chin_structure"), ("Forehead", "forehead_proportions"),
        ("Geometry", "facial_geometry_notes"),
        ("Architecture", "facial_architecture_summary"),
    ]:
        out.append(f"- **{label}:** {s(fs.get(key))}")
    out.append("")

    # ---- Skin
    sk = data.get("skin_analysis", {}) or {}
    out.append("## Skin Analysis")
    for label, key in [
        ("Skin tone", "skin_tone"), ("Undertone", "undertone"),
        ("Texture", "texture"), ("Condition", "condition"),
        ("Acne", "acne_observation"), ("Dark circles", "dark_circles"),
        ("Redness", "redness"), ("Wrinkles", "wrinkles"), ("Pores", "pores"),
    ]:
        out.append(f"- **{label}:** {s(sk.get(key))}")
    out.append(f"- **Smoothness:** {s(sk.get('smoothness_score'))}/100")
    out.append(f"- **Skin health:** {s(sk.get('overall_skin_health_score'))}/100\n")

    # ---- Beard
    bd = data.get("beard_analysis", {}) or {}
    out.append("## Beard Analysis")
    for label, key in [
        ("Has beard", "has_beard"), ("Style", "style"),
        ("Density", "density"), ("Length", "length"),
        ("Grooming", "grooming_condition"),
    ]:
        out.append(f"- **{label}:** {s(bd.get(key))}")
    out.append("")

    # ---- Hair
    h = data.get("hair_analysis", {}) or {}
    out.append("## Hair Analysis")
    for label, key in [
        ("Current style", "current_hairstyle"), ("Length observed", "length_observed"),
        ("Texture", "texture_classification"), ("Pattern", "pattern"),
        ("Density", "density"), ("Thickness", "thickness"), ("Volume", "volume"),
        ("Hairline", "hairline_condition"), ("Curl pattern", "curl_pattern"),
        ("Growth direction", "growth_direction"), ("Shine", "shine_level"),
        ("Frizz", "frizz_level"), ("Damage", "damage_observation"),
        ("Thinning", "thinning_observation"), ("Split ends", "split_ends"),
        ("Dry/Oily", "dry_or_oily"), ("Scalp visibility", "scalp_visibility"),
    ]:
        out.append(f"- **{label}:** {s(h.get(key))}")
    out.append(f"- **Hair health:** {s(h.get('hair_health_score'))}/100\n")

    # ---- Hair color
    hc = data.get("hair_color_analysis", {}) or {}
    out.append("## Hair Color Analysis")
    for label, key in [
        ("Current color", "current_color"), ("Tone", "tone"),
        ("Warm/Cool", "warm_cool_balance"),
        ("Natural color (est.)", "estimated_natural_color"),
        ("Depth", "color_depth"),
    ]:
        out.append(f"- **{label}:** {s(hc.get(key))}")
    out.append("")

    # ---- Trend
    st = data.get("style_trend_analysis", {}) or {}
    out.append("## Style & Trend")
    out.append(f"- **Classification:** {s(st.get('current_classification'))} "
               f"({s(st.get('trend_score'))}/100)")
    out.append(f"- **Celebrity-inspired category:** "
               f"{s(st.get('celebrity_inspired_category'))}\n")

    # ---- Recommendations: hairstyles
    rec = data.get("recommendations", {}) or {}
    out.append("## Hairstyle Recommendations")
    for i, hs in enumerate(rec.get("hairstyles") or [], 1):
        out.append(f"### {i}. {s(hs.get('name'))} "
                   f"— {s(hs.get('compatibility_score'))}/100")
        if hs.get("description"):
            out.append(f"_{hs['description']}_")
        out.append(f"- **Why it suits:** {s(hs.get('why_it_suits'))}")
        out.append(f"- **Difficulty:** {s(hs.get('styling_difficulty'))}  |  "
                   f"**Maintenance:** {s(hs.get('maintenance_level'))}  |  "
                   f"**Suitability:** {s(hs.get('suitability'))}")
        if hs.get("styling_tips"):
            out.append("- **Tips:**\n" +
                       "\n".join(f"  - {t}" for t in hs["styling_tips"]))
        tutorials = hs.get("tutorials") or []
        if tutorials:
            out.append("- **Tutorials:**")
            for tutorial in tutorials:
                title = s(tutorial.get("title"))
                url = s(tutorial.get("url"))
                out.append(f"  - [{title}]({url})")
        out.append("")

    # ---- Hair colors
    hcr = rec.get("hair_colors", {}) or {}
    out.append("## Hair Color Recommendations")
    for label, key in [
        ("Best matching", "best_matching"), ("Natural options", "natural_options"),
        ("Bold options", "bold_options"), ("Colors to avoid", "colors_to_avoid"),
    ]:
        items = hcr.get(key) or []
        if items:
            out.append(f"- **{label}:** {', '.join(map(str, items))}")
    if hcr.get("reasoning"):
        out.append(f"\n_Reasoning:_ {hcr['reasoning']}")
    out.append("")

    # ---- Beard recs
    br = rec.get("beard_recommendations") or []
    if br:
        out.append("## Beard Recommendations")
        for b in br:
            out.append(f"- **{s(b.get('style'))}** "
                       f"({s(b.get('compatibility_score'))}/100) — "
                       f"{s(b.get('why_it_suits'))}")
        out.append("")

    # ---- Hair care
    hcare = rec.get("hair_care", {}) or {}
    if hcare:
        out.append("## Hair Care & Treatment")
        for label, key in [
            ("Growth", "growth_suggestions"), ("Repair", "repair_suggestions"),
            ("Hair fall prevention", "hair_fall_prevention"),
            ("Scalp care", "scalp_care"), ("Home remedies", "home_remedies"),
            ("Routine", "maintenance_routine"),
        ]:
            items = hcare.get(key) or []
            if items:
                out.append(f"\n**{label}:**\n" + _bullets(items))
        tutorials = hcare.get("tutorials") or []
        if tutorials:
            out.append("\n**Tutorials:**")
            for tutorial in tutorials:
                title = s(tutorial.get("title"))
                url = s(tutorial.get("url"))
                out.append(f"- [{title}]({url})")
        prods = hcare.get("product_recommendations", {}) or {}
        if any(prods.values()):
            out.append("\n**Products:**")
            for k, v in prods.items():
                if v:
                    out.append(f"- _{k.replace('_', ' ').title()}:_ "
                               f"{', '.join(map(str, v))}")
        out.append("")

    # ---- Face care
    fc = rec.get("face_care", {}) or {}
    if fc:
        out.append("## Face Care Recommendations")
        for label, key in [
            ("Skin care", "skin_care_advice"), ("Acne prevention", "acne_prevention"),
            ("Hydration", "hydration"), ("Texture", "texture_improvement"),
            ("Grooming", "grooming_advice"),
        ]:
            items = fc.get(key) or []
            if items:
                out.append(f"\n**{label}:**\n" + _bullets(items))
        out.append("")

    return "\n".join(out)


def save_results(data: dict, base_name: str) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"{base_name}_{ts}.json"
    md_path = OUTPUT_DIR / f"{base_name}_{ts}.md"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(to_markdown(data), encoding="utf-8")
    return json_path, md_path


# ─────────────────────────────────────────────────────────────────────────────
# CLI ENTRY
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("  Face & Hair AI Analysis Tool")
    print("=" * 60)
    print(f"  Using Model: {MODEL}")
    print("=" * 60)
    print()
    
    # Check if API key is set
    if not API_KEY or API_KEY == "your_openai_api_key_here":
        print("⚠️  ERROR: OpenAI API key not configured!")
        print()
        print("Please follow these steps:")
        print("1. Open the '.env' file in this directory")
        print("2. Replace 'your_openai_api_key_here' with your actual API key")
        print("3. Get your API key from: https://platform.openai.com/api-keys")
        print()
        print("Example .env file:")
        print("  OPENAI_API_KEY=sk-proj-abc123...")
        print("  OPENAI_MODEL=gpt-4o")
        print()
        sys.exit(1)
    
    # Get image path
    if len(sys.argv) > 1:
        image_input = sys.argv[1]
    else:
        # Show available images in current directory
        current_dir = Path(".")
        image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
        available_images = [f for f in current_dir.iterdir() 
                          if f.is_file() and f.suffix.lower() in image_extensions]
        
        if available_images:
            print("Available images in current directory:")
            for img in sorted(available_images):
                print(f"  - {img.name}")
            print()
        
        image_input = input("Enter image filename (e.g., 1.png): ").strip()
    
    image_path = Path(image_input).expanduser().resolve()
    
    if not image_path.exists():
        print(f"❌ Error: Image not found at {image_path}")
        sys.exit(1)
    
    # Validate image format
    ext = image_path.suffix.lower().lstrip(".")
    if ext == "jpg":
        ext = "jpeg"
    if ext not in {"jpeg", "png", "webp", "gif"}:
        print(f"❌ Error: Unsupported image format '.{image_path.suffix}'")
        print(f"   Supported formats: .jpg, .jpeg, .png, .webp, .gif")
        print(f"   You entered: {image_path.name}")
        sys.exit(1)
    
    # Get gender
    if len(sys.argv) > 2:
        gender = sys.argv[2].lower()
    else:
        while True:
            gender = input("Enter gender (male/female): ").strip().lower()
            if gender in {"male", "female"}:
                break
            print("Error: Please enter 'male' or 'female'")
    
    # Get hair length
    if len(sys.argv) > 3:
        hair_length = sys.argv[3].lower()
    else:
        while True:
            hair_length = input("Enter hair length (short/medium/long): ").strip().lower()
            if hair_length in {"short", "medium", "long"}:
                break
            print("Error: Please enter 'short', 'medium', or 'long'")
    
    print()
    print("-" * 60)

    print(f"Analyzing {image_path.name} ...")
    try:
        data = enrich_analysis_with_tutorials(analyze(image_path, gender, hair_length))
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(2)

    json_path, md_path = save_results(data, image_path.stem)

    # Quick console snapshot
    fs = data.get("face_shape_analysis", {}) or {}
    h = data.get("hair_analysis", {}) or {}
    sk = data.get("skin_analysis", {}) or {}
    print()
    print(f"Face shape : {fs.get('detected_shape')} ({fs.get('confidence_score')}/100)")
    print(f"Skin tone  : {sk.get('skin_tone')} ({sk.get('undertone')})")
    print(f"Hair       : {h.get('texture_classification')}, "
          f"density {h.get('density')}, health {h.get('hair_health_score')}/100")
    print()
    print("Top hairstyles:")
    for i, hs in enumerate((data.get("recommendations") or {}).get("hairstyles") or [], 1):
        print(f"  {i}. {hs.get('name')} — {hs.get('compatibility_score')}/100")
    print()
    print("-" * 60)
    print(f"✓ JSON saved : {json_path}")
    print(f"✓ Report     : {md_path}")
    print("-" * 60)
    print("\nAnalysis complete! Check the reports folder for detailed results.")
    print()


if __name__ == "__main__":
    main()