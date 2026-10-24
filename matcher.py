"""
matcher.py - Explainable Smart Matching Algorithm for Lost & Found Items
------------------------------------------------------------------------
Author: College Innovation Project
Purpose: Implements a rule-based weighted scoring engine (0-100) and an optional
         NLP semantic matching enhancement to identify potential item matches.
"""

import re
from datetime import datetime
from difflib import SequenceMatcher

# Common English stopwords to remove during token comparison
STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "with", "and", "or", "for", "of",
    "to", "is", "it", "my", "has", "have", "had", "near", "by", "from",
    "some", "this", "that", "there", "left", "found", "lost", "area", "zone"
}

# Campus synonym clusters for the Optional Semantic / NLP Enhancement
# Allows the algorithm to understand that "bottle" and "flask" or "earbuds" and "earpods" refer to the same item
SEMANTIC_SYNONYMS = {
    "bottle": {"bottle", "flask", "tumbler", "hydroflask", "thermos", "sipper", "waterbottle", "container"},
    "flask": {"bottle", "flask", "tumbler", "hydroflask", "thermos", "sipper", "waterbottle"},
    "earbuds": {"earbuds", "earphones", "earpods", "headphones", "buds", "airpods", "headset"},
    "earphones": {"earbuds", "earphones", "earpods", "headphones", "buds", "airpods", "headset"},
    "airpods": {"earbuds", "earphones", "earpods", "headphones", "buds", "airpods"},
    "lanyard": {"lanyard", "strap", "neckband", "cord", "badgeholder", "neck", "ribbon"},
    "id": {"id", "card", "badge", "identity", "pass"},
    "notebook": {"notebook", "register", "copy", "diary", "journal", "pad", "binder"},
    "umbrella": {"umbrella", "parasol", "brolly", "rainshade"},
    "backpack": {"backpack", "bag", "rucksack", "knapsack", "satchel"},
    "keys": {"keys", "keychain", "keyring", "fob", "key"},
    "black": {"black", "dark", "charcoal", "matte", "jet"},
    "blue": {"blue", "navy", "cyan", "azure", "cobalt", "indigo"},
    "white": {"white", "silver", "cream", "ivory", "light"},
    "grey": {"grey", "gray", "silver", "ash", "metallic"},
    "green": {"green", "olive", "emerald", "lime"},
    "red": {"red", "maroon", "crimson", "burgundy"}
}


def normalize_text(text: str) -> str:
    """
    Cleans raw text by converting to lowercase, removing punctuation,
    and stripping consecutive whitespace.
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def extract_keywords(text: str) -> set:
    """
    Splits text into meaningful word tokens, discarding common stopwords
    and single-letter characters.
    """
    clean = normalize_text(text)
    tokens = clean.split()
    return {w for w in tokens if w not in STOPWORDS and len(w) > 1}


def string_similarity(a: str, b: str) -> float:
    """
    Calculates normalized character-level Levenshtein similarity ratio between two strings (0.0 to 1.0).
    Uses Python's standard difflib.SequenceMatcher.
    """
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def check_synonym_match(word1: str, word2: str) -> bool:
    """
    Checks if two words share a semantic category in the synonym clusters.
    """
    if word1 == word2:
        return True
    for key, syn_set in SEMANTIC_SYNONYMS.items():
        if word1 in syn_set and word2 in syn_set:
            return True
    return False


def score_category(lost_cat: str, found_cat: str) -> tuple[int, str]:
    """
    Factor 1: Category Match (Maximum: 30 Points)
    Item category is the strongest discriminator. If items are in different
    categories, they are almost certainly not the same item.
    """
    norm_lost = normalize_text(lost_cat)
    norm_found = normalize_text(found_cat)

    if norm_lost == norm_found and norm_lost:
        return 30, f"Exact category match ({lost_cat})"
    elif norm_lost in norm_found or norm_found in norm_lost:
        return 20, f"Compatible category overlap ({lost_cat} ≈ {found_cat})"
    else:
        return 0, f"Category mismatch ('{lost_cat}' vs '{found_cat}')"


def score_title(lost_title: str, found_title: str, use_nlp: bool = False) -> tuple[int, str]:
    """
    Factor 2: Title and Item Name Similarity (Maximum: 25 Points)
    Compares the core names given to the items.
    """
    kw_lost = extract_keywords(lost_title)
    kw_found = extract_keywords(found_title)

    if not kw_lost or not kw_found:
        return 0, "No descriptive title keywords to compare"

    # Direct token intersection
    intersection = kw_lost.intersection(kw_found)
    nlp_semantic_matches = set()

    if use_nlp:
        # Check for semantic synonyms across keywords
        for w1 in kw_lost:
            for w2 in kw_found:
                if w1 != w2 and check_synonym_match(w1, w2):
                    nlp_semantic_matches.add(f"{w1}≈{w2}")

    overlap_count = len(intersection) + len(nlp_semantic_matches)
    ratio = overlap_count / max(1, min(len(kw_lost), len(kw_found)))

    # String fuzzy similarity as a secondary check
    fuzzy_ratio = string_similarity(lost_title, found_title)

    # Combined score calculation
    raw_score = (ratio * 18.0) + (fuzzy_ratio * 7.0)
    score = min(25, round(raw_score))

    details = []
    if intersection:
        details.append(f"Matching words: {', '.join(sorted(intersection))}")
    if nlp_semantic_matches:
        details.append(f"Semantic synonyms recognized: {', '.join(sorted(nlp_semantic_matches))}")
    if not details:
        details.append(f"Title similarity index: {int(fuzzy_ratio * 100)}%")

    return score, " | ".join(details)


def score_description(lost_desc: str, found_desc: str, use_nlp: bool = False) -> tuple[int, str]:
    """
    Factor 3: Distinguishing Features & Description (Maximum: 20 Points)
    Examines scratches, stickers, marks, brands, and fine details.
    """
    kw_lost = extract_keywords(lost_desc)
    kw_found = extract_keywords(found_desc)

    if not kw_lost or not kw_found:
        return 5, "Limited description provided by one or both parties"

    intersection = kw_lost.intersection(kw_found)
    nlp_matches = set()

    if use_nlp:
        for w1 in kw_lost:
            for w2 in kw_found:
                if w1 != w2 and check_synonym_match(w1, w2):
                    nlp_matches.add(f"{w1}≈{w2}")

    combined_overlap = len(intersection) + len(nlp_matches)

    # High-value feature keywords that carry strong evidential weight
    feature_keywords = {"sticker", "scratch", "dent", "broken", "initials", "name",
                        "logo", "strap", "case", "chain", "ring", "mark", "cord", "badge"}
    key_features_found = (kw_lost | kw_found).intersection(feature_keywords)

    score = 0
    if combined_overlap > 0:
        score += min(14, combined_overlap * 4)
    if key_features_found and (intersection or nlp_matches):
        score += 6  # Bonus for matching specific distinguishing marks!

    score = min(20, max(0, score))

    details = []
    if intersection:
        details.append(f"Shared details: {', '.join(list(intersection)[:4])}")
    if nlp_matches:
        details.append(f"NLP detail overlap: {', '.join(list(nlp_matches)[:3])}")
    if not details:
        details.append("General descriptions compared (no unique feature tokens shared)")

    return score, " | ".join(details)


def score_color(lost_color: str, found_color: str, lost_desc: str = "", found_desc: str = "") -> tuple[int, str]:
    """
    Factor 4: Colour Match (Maximum: 15 Points)
    Checks explicit color fields and verifies if color words appear in descriptions.
    """
    norm_lost = normalize_text(lost_color)
    norm_found = normalize_text(found_color)

    # Exact color match
    if norm_lost and norm_found and norm_lost == norm_found:
        return 15, f"Exact color match ({lost_color})"

    # Check for color synonyms (e.g. navy blue vs blue, dark vs black)
    tokens_lost = set(norm_lost.split())
    tokens_found = set(norm_found.split())

    if tokens_lost.intersection(tokens_found):
        return 12, f"Partial color overlap ('{lost_color}' & '{found_color}')"

    # Check synonym groups for colors
    for w1 in tokens_lost:
        for w2 in tokens_found:
            if check_synonym_match(w1, w2):
                return 10, f"Color tone match ('{w1}' ≈ '{w2}')"

    # Check if lost color is mentioned in found description or vice-versa
    if norm_lost and norm_lost in normalize_text(found_desc):
        return 8, f"Lost color '{lost_color}' referenced in found item description"
    if norm_found and norm_found in normalize_text(lost_desc):
        return 8, f"Found color '{found_color}' referenced in lost item description"

    return 0, f"Different colors reported ('{lost_color}' vs '{found_color}')"


def score_location(lost_loc: str, found_loc: str) -> tuple[int, str]:
    """
    Factor 5: Campus Location Proximity (Maximum: 10 Points)
    Compares campus buildings, floors, and landmarks.
    """
    norm_lost = normalize_text(lost_loc)
    norm_found = normalize_text(found_loc)

    if norm_lost == norm_found and norm_lost:
        return 10, f"Exact same location ({lost_loc})"

    kw_lost = extract_keywords(lost_loc)
    kw_found = extract_keywords(found_loc)
    common_loc = kw_lost.intersection(kw_found)

    # Key campus hubs
    major_zones = {"library", "cafeteria", "canteen", "lab", "gymnasium", "sports",
                   "hostel", "hall", "gate", "auditorium", "quad", "ground"}

    shared_major = common_loc.intersection(major_zones)

    if shared_major:
        return 8, f"Same campus zone ({', '.join(shared_major).title()})"
    elif common_loc:
        return 5, f"Nearby location keyword match ({', '.join(common_loc)})"
    else:
        return 1, f"Different campus spots ('{lost_loc}' vs '{found_loc}')"


def check_date_plausibility(lost_date_str: str, found_date_str: str) -> tuple[int, str, bool]:
    """
    Evaluates date consistency.
    An item cannot realistically be found weeks before it was lost.
    Returns: (penalty_or_bonus_points, explanation_text, is_plausible_bool)
    """
    try:
        d_lost = datetime.strptime(lost_date_str.strip()[:10], "%Y-%m-%d").date()
        d_found = datetime.strptime(found_date_str.strip()[:10], "%Y-%m-%d").date()

        diff_days = (d_found - d_lost).days

        if diff_days >= 0:
            if diff_days <= 3:
                return 0, f"Found {diff_days} day(s) after being lost (ideal timeline)", True
            elif diff_days <= 14:
                return 0, f"Found within {diff_days} days of lost date", True
            else:
                return -5, f"Found {diff_days} days after lost date (possible delay in reporting)", True
        else:
            # Found date is before lost date
            if abs(diff_days) <= 1:
                return 0, "Dates match closely (within 24 hours / timezone variance)", True
            else:
                return -10, f"Date anomaly: Item was reported found {abs(diff_days)} days before lost date", False
    except Exception:
        return 0, "Date format unverified; no penalty applied", True


def calculate_match(lost_item: dict, found_item: dict, use_nlp: bool = False) -> dict:
    """
    Main matching function:
    Compares one LOST item report against one FOUND item report.
    Returns a structured dictionary with total score (0-100), factor breakdowns,
    confidence rating, and an ownership verification advisory.
    """
    breakdown = []

    # 1. Category (30 pts)
    cat_score, cat_detail = score_category(lost_item.get("category", ""), found_item.get("category", ""))
    breakdown.append({
        "factor": "Item Category",
        "score": cat_score,
        "max": 30,
        "detail": cat_detail
    })

    # If category completely mismatches, the items are different objects
    if cat_score == 0:
        total_score = 0
        confidence = "No Match"
        reasons = [cat_detail]
        return {
            "total_score": 0,
            "confidence": confidence,
            "breakdown": breakdown,
            "reasons": reasons,
            "warning": "Item types do not align.",
            "is_suggested": False,
            "lost_item": lost_item,
            "found_item": found_item
        }

    # 2. Title & Name (25 pts)
    title_score, title_detail = score_title(
        lost_item.get("title", ""),
        found_item.get("title", ""),
        use_nlp=use_nlp
    )
    breakdown.append({
        "factor": "Item Title & Name",
        "score": title_score,
        "max": 25,
        "detail": title_detail
    })

    # 3. Description & Distinguishing Features (20 pts)
    desc_score, desc_detail = score_description(
        lost_item.get("description", ""),
        found_item.get("description", ""),
        use_nlp=use_nlp
    )
    breakdown.append({
        "factor": "Distinguishing Features",
        "score": desc_score,
        "max": 20,
        "detail": desc_detail
    })

    # 4. Colour (15 pts)
    color_score, color_detail = score_color(
        lost_item.get("color", ""),
        found_item.get("color", ""),
        lost_item.get("description", ""),
        found_item.get("description", "")
    )
    breakdown.append({
        "factor": "Colour Match",
        "score": color_score,
        "max": 15,
        "detail": color_detail
    })

    # 5. Location (10 pts)
    loc_score, loc_detail = score_location(
        lost_item.get("location", ""),
        found_item.get("location", "")
    )
    breakdown.append({
        "factor": "Campus Location",
        "score": loc_score,
        "max": 10,
        "detail": loc_detail
    })

    # 6. Date Plausibility Check (Modifier: 0 to -10)
    date_adj, date_detail, date_plausible = check_date_plausibility(
        lost_item.get("date_event", ""),
        found_item.get("date_event", "")
    )
    breakdown.append({
        "factor": "Date Timeline Consistency",
        "score": max(0, 5 + date_adj) if date_adj < 0 else 5,
        "max": 5,
        "detail": date_detail
    })

    # Calculate raw sum (0 - 100)
    raw_total = cat_score + title_score + desc_score + color_score + loc_score + date_adj
    total_score = max(0, min(100, int(round(raw_total))))

    # Determine confidence tier
    if total_score >= 75:
        confidence = "High Match"
        is_suggested = True
    elif total_score >= 50:
        confidence = "Moderate Match"
        is_suggested = True
    elif total_score >= 35:
        confidence = "Low Match (Partial)"
        is_suggested = False
    else:
        confidence = "Unlikely Match"
        is_suggested = False

    reasons = [b["detail"] for b in breakdown if b["score"] > 0]

    warning_text = (
        "Important Security Reminder: A suggested match is NOT proof of ownership. "
        "Claimants must verify secret identifying marks, serial numbers, or show "
        "matching proof before an item is returned."
    )

    return {
        "total_score": total_score,
        "confidence": confidence,
        "breakdown": breakdown,
        "reasons": reasons,
        "warning": warning_text,
        "is_suggested": is_suggested,
        "date_plausible": date_plausible,
        "lost_item": lost_item,
        "found_item": found_item
    }


def find_all_matches(reports: list, min_score: int = 40, use_nlp: bool = False) -> list:
    """
    Compares every OPEN lost report against every OPEN found report.
    Returns a sorted list of matches (highest score first) without duplicates.
    """
    lost_items = [r for r in reports if r.get("type") == "LOST" and r.get("status") != "RESOLVED"]
    found_items = [r for r in reports if r.get("type") == "FOUND" and r.get("status") != "RESOLVED"]

    matches = []
    seen_pairs = set()

    for lost in lost_items:
        for found in found_items:
            pair_key = (lost["id"], found["id"])
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            res = calculate_match(lost, found, use_nlp=use_nlp)
            if res["total_score"] >= min_score:
                matches.append(res)

    # Sort descending by match score
    matches.sort(key=lambda m: m["total_score"], reverse=True)
    return matches
