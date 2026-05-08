import re
import json
from typing import Dict, Tuple
import math
from collections import Counter

# --- Load datasets ---
with open("msc5.json", "r", encoding="utf-8") as f:
    PREFIX_5_DB = json.load(f)

with open("msc4.json", "r", encoding="utf-8") as f:
    PREFIX_4_DB = json.load(f)


def extract_features(num: str, carrier_data: dict) -> dict:
    features = {}

    # ---------------------------------------------------
    # Basic telecom features
    # ---------------------------------------------------

    features["length"] = len(num)

    features["starts_valid"] = num[0] in "6789"

    features["has_valid_5digit_msc"] = (
        carrier_data.get("match_length") == 5
    )

    features["has_valid_4digit_msc"] = (
        carrier_data.get("match_length") == 4
    )

    features["carrier_known"] = (
        carrier_data.get("carrier") != "Unknown"
    )

    features["circle_known"] = (
        carrier_data.get("circle") != "Unknown"
    )

    # ---------------------------------------------------
    # Digit analysis
    # ---------------------------------------------------

    digit_counts = Counter(num)

    features["unique_digits"] = len(digit_counts)

    features["most_common_digit_count"] = (
        max(digit_counts.values())
    )

    features["repeated_digit_ratio"] = (
        features["most_common_digit_count"] / len(num)
    )

    # ---------------------------------------------------
    # Entropy calculation
    # ---------------------------------------------------

    entropy = 0.0

    for count in digit_counts.values():
        p = count / len(num)
        entropy -= p * math.log2(p)

    features["digit_entropy"] = round(entropy, 4)

    # ---------------------------------------------------
    # Sequential pattern detection
    # ---------------------------------------------------

    ascending = "01234567890"
    descending = "9876543210"

    features["is_sequential_ascending"] = (
        num in ascending
    )

    features["is_sequential_descending"] = (
        num in descending
    )

    # ---------------------------------------------------
    # Repeating chunk patterns
    # ---------------------------------------------------

    features["has_repeating_2digit_pattern"] = (
        num[:2] * 5 == num
    )

    features["has_repeating_3digit_pattern"] = (
        num[:3] * 3 in num
    )

    # ---------------------------------------------------
    # Mirror symmetry
    # ---------------------------------------------------

    features["is_mirrored"] = (
        num == num[::-1]
    )

    # ---------------------------------------------------
    # Consecutive repeated runs
    # ---------------------------------------------------

    max_run = 1
    current_run = 1

    for i in range(1, len(num)):
        if num[i] == num[i - 1]:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1

    features["max_consecutive_run"] = max_run

    # ---------------------------------------------------
    # Suspicious telecom heuristics
    # ---------------------------------------------------

    features["starts_with_99999"] = (
        num.startswith("99999")
    )

    features["starts_with_12345"] = (
        num.startswith("12345")
    )

    features["starts_with_00000"] = (
        num.startswith("00000")
    )

    # ---------------------------------------------------
    # Human-looking score
    # ---------------------------------------------------

    human_score = 100

    if features["digit_entropy"] < 2:
        human_score -= 40

    if features["max_consecutive_run"] >= 5:
        human_score -= 25

    if features["is_sequential_ascending"]:
        human_score -= 35

    if features["is_sequential_descending"]:
        human_score -= 35

    if features["has_repeating_2digit_pattern"]:
        human_score -= 30

    if features["is_mirrored"]:
        human_score -= 20

    features["human_probability_score"] = max(human_score, 0)

    return features

def estimate_reachability(features: dict) -> dict:
    probability = 0.50
    confidence = 0.50

    reasons = []

    # ---------------------------------------------------
    # Telecom validity
    # ---------------------------------------------------

    if features["carrier_known"]:
        probability += 0.20
        confidence += 0.15
        reasons.append("known_carrier")

    if features["circle_known"]:
        probability += 0.10
        confidence += 0.05
        reasons.append("known_circle")

    if features["has_valid_5digit_msc"]:
        probability += 0.08
        confidence += 0.08
        reasons.append("5digit_msc_match")

    elif features["has_valid_4digit_msc"]:
        probability += 0.04
        confidence += 0.04
        reasons.append("4digit_msc_match")

    # ---------------------------------------------------
    # Entropy / realism
    # ---------------------------------------------------

    entropy = features["digit_entropy"]

    if entropy >= 2.8:
        probability += 0.12
        reasons.append("healthy_entropy")

    elif entropy < 2.0:
        probability -= 0.25
        confidence += 0.10
        reasons.append("low_entropy")

    # ---------------------------------------------------
    # Repeated digit analysis
    # ---------------------------------------------------

    if features["max_consecutive_run"] >= 6:
        probability -= 0.30
        confidence += 0.10
        reasons.append("extreme_repetition")

    elif features["max_consecutive_run"] >= 4:
        probability -= 0.12
        reasons.append("moderate_repetition")

    # ---------------------------------------------------
    # Sequential patterns
    # ---------------------------------------------------

    if features["is_sequential_ascending"]:
        probability -= 0.35
        confidence += 0.15
        reasons.append("ascending_sequence")

    if features["is_sequential_descending"]:
        probability -= 0.35
        confidence += 0.15
        reasons.append("descending_sequence")

    # ---------------------------------------------------
    # Pattern repetition
    # ---------------------------------------------------

    if features["has_repeating_2digit_pattern"]:
        probability -= 0.20
        reasons.append("repeating_2digit_pattern")

    if features["has_repeating_3digit_pattern"]:
        probability -= 0.15
        reasons.append("repeating_3digit_pattern")

    # ---------------------------------------------------
    # Suspicious prefixes
    # ---------------------------------------------------

    if features["starts_with_00000"]:
        probability -= 0.40
        confidence += 0.20
        reasons.append("invalid_zero_prefix")

    if features["starts_with_12345"]:
        probability -= 0.25
        reasons.append("fake_test_pattern")

    # ---------------------------------------------------
    # Human-likelihood contribution
    # ---------------------------------------------------

    human_score = features["human_probability_score"]

    probability += ((human_score - 50) / 100) * 0.20

    # ---------------------------------------------------
    # Clamp outputs
    # ---------------------------------------------------

    probability = round(
        max(min(probability, 1.0), 0.0),
        2
    )

    confidence = round(
        max(min(confidence, 1.0), 0.0),
        2
    )

    # ---------------------------------------------------
    # Risk labels
    # ---------------------------------------------------

    if probability >= 0.80:
        level = "high"

    elif probability >= 0.55:
        level = "medium"

    else:
        level = "low"

    return {
        "reachability_probability": probability,
        "reachability_confidence": confidence,
        "reachability_level": level,
        "reachability_reasons": reasons,
    }

# --- Normalization ---
def normalize(phone: str) -> dict:
    """
    Infer and normalize phone numbers from messy input.
    """

    raw = phone

    digits = re.sub(r"\D", "", phone)

    result = {
        "raw_input": raw,
        "digits": digits,
        "normalized": None,
        "country_code": None,
        "inferred_country": None,
        "parse_confidence": 0.0,
        "parse_strategy": None,
    }

    # ---------------------------------------------------
    # Indian local mobile
    # Example:
    # 9876543210
    # ---------------------------------------------------

    if (
        len(digits) == 10 and
        digits[0] in "6789"
    ):
        result.update({
            "normalized": "+91" + digits,
            "country_code": "91",
            "inferred_country": "IN",
            "parse_confidence": 0.95,
            "parse_strategy": "indian_local_mobile"
        })

        return result

    # ---------------------------------------------------
    # Indian with country code
    # Example:
    # 919876543210
    # ---------------------------------------------------

    if (
        len(digits) == 12 and
        digits.startswith("91")
    ):
        local = digits[2:]

        if local[0] in "6789":

            result.update({
                "normalized": "+" + digits,
                "country_code": "91",
                "inferred_country": "IN",
                "parse_confidence": 0.98,
                "parse_strategy": "indian_cc_mobile"
            })

            return result

    # ---------------------------------------------------
    # International-like
    # ---------------------------------------------------

    if 8 <= len(digits) <= 15:

        result.update({
            "normalized": "+" + digits,
            "country_code": "unknown",
            "inferred_country": "unknown",
            "parse_confidence": 0.40,
            "parse_strategy": "generic_international"
        })

        return result

    # ---------------------------------------------------
    # Failed parse
    # ---------------------------------------------------

    result.update({
        "parse_strategy": "unrecognized",
        "parse_confidence": 0.0
    })

    return result


# --- Validation ---
def classify_number(normalized_data: dict) -> dict:

    normalized = normalized_data["normalized"]

    if not normalized:
        return {
            "is_valid": False,
            "type": "invalid"
        }

    digits = normalized.replace("+", "")

    # India
    if digits.startswith("91"):

        local = digits[2:]

        if (
            len(local) == 10 and
            local[0] in "6789"
        ):
            return {
                "is_valid": True,
                "type": "indian_mobile"
            }

        return {
            "is_valid": False,
            "type": "invalid_indian"
        }

    # Generic international
    if 8 <= len(digits) <= 15:
        return {
            "is_valid": True,
            "type": "international"
        }

    return {
        "is_valid": False,
        "type": "invalid"
    }


# --- Prefix lookup (5-digit first, then 4-digit fallback) ---
def lookup_prefix(num: str) -> Dict[str, str]:
    prefix5 = num[:5]
    prefix4 = num[:4]

    # Try 5-digit lookup first
    if prefix5 in PREFIX_5_DB:
        data = PREFIX_5_DB[prefix5]
        data["match_length"] = 5
        data["matched_prefix"] = prefix5
        return data

    # Fallback to 4-digit lookup
    if prefix4 in PREFIX_4_DB:
        data = PREFIX_4_DB[prefix4]
        data["match_length"] = 4
        data["matched_prefix"] = prefix4
        return data

    return {
        "carrier": "Unknown",
        "circle": "Unknown",
        "match_length": 0,
        "matched_prefix": None,
    }


# --- Spam scoring ---
def calculate_risk(features: dict) -> tuple[int, list]:
    score = 0
    flags = []

    if features["digit_entropy"] < 2:
        score += 30
        flags.append("low_entropy")

    if features["max_consecutive_run"] >= 5:
        score += 25
        flags.append("long_repeated_run")

    if features["is_sequential_ascending"]:
        score += 40
        flags.append("ascending_sequence")

    if features["is_sequential_descending"]:
        score += 40
        flags.append("descending_sequence")

    if features["has_repeating_2digit_pattern"]:
        score += 25
        flags.append("repeating_pattern")

    if not features["carrier_known"]:
        score += 20
        flags.append("unknown_carrier")

    return min(score, 100), flags


# --- WhatsApp likelihood ---
def estimate_whatsapp(features: dict, reachability: dict) -> dict:

    probability = 0.65
    confidence = 0.50

    reasons = []

    # ---------------------------------------------------
    # Reachability contribution
    # ---------------------------------------------------

    reach_prob = reachability["reachability_probability"]

    probability += (reach_prob - 0.5) * 0.60

    if reach_prob >= 0.80:
        confidence += 0.20
        reasons.append("high_reachability")

    elif reach_prob <= 0.30:
        confidence += 0.15
        reasons.append("low_reachability")

    # ---------------------------------------------------
    # Telecom validity
    # ---------------------------------------------------

    if features["carrier_known"]:
        probability += 0.10
        confidence += 0.10
        reasons.append("known_carrier")

    if features["circle_known"]:
        probability += 0.05
        reasons.append("known_circle")

    # ---------------------------------------------------
    # Entropy analysis
    # ---------------------------------------------------

    entropy = features["digit_entropy"]

    if entropy >= 2.8:
        probability += 0.08
        reasons.append("healthy_entropy")

    elif entropy < 2.0:
        probability -= 0.25
        confidence += 0.10
        reasons.append("low_entropy")

    # ---------------------------------------------------
    # Suspicious patterns
    # ---------------------------------------------------

    if features["is_sequential_ascending"]:
        probability -= 0.35
        confidence += 0.15
        reasons.append("ascending_sequence")

    if features["is_sequential_descending"]:
        probability -= 0.35
        confidence += 0.15
        reasons.append("descending_sequence")

    if features["has_repeating_2digit_pattern"]:
        probability -= 0.20
        reasons.append("repeating_pattern")

    if features["max_consecutive_run"] >= 6:
        probability -= 0.30
        confidence += 0.15
        reasons.append("extreme_repetition")

    # ---------------------------------------------------
    # Human-likelihood adjustment
    # ---------------------------------------------------

    human_score = features["human_probability_score"]

    probability += ((human_score - 50) / 100) * 0.15

    # ---------------------------------------------------
    # Clamp
    # ---------------------------------------------------

    probability = round(
        max(min(probability, 1.0), 0.0),
        2
    )

    confidence = round(
        max(min(confidence, 1.0), 0.0),
        2
    )

    # ---------------------------------------------------
    # Classification
    # ---------------------------------------------------

    if probability >= 0.90:
        level = "very_likely"

    elif probability >= 0.80:
        level = "likely"

    elif probability >= 0.60:
        level = "not_confident"

    else:
        level = "unlikely"

    return {
        "whatsapp_probability": probability,
        "whatsapp_confidence": confidence,
        "whatsapp_likelihood": level,
        "whatsapp_reasons": reasons,
    }


# --- Main analyzer ---
def analyze_phone(phone: str) -> dict:
    """
    Main intelligence pipeline.
    """

    # ---------------------------------------------------
    # Step 1: Normalize / infer input
    # ---------------------------------------------------

    normalization = normalize(phone)

    # ---------------------------------------------------
    # Step 2: Classify number
    # ---------------------------------------------------

    classification = classify_number(normalization)

    if classification["type"] == "international":

        local = normalization["digits"]

        features = extract_features(
            local,
            {
                "carrier": "Unknown",
                "circle": "Unknown",
                "match_length": 0,
                "matched_prefix": None,
            }
        )

        risk_score, risk_flags = calculate_risk(
            features
        )

        response = ({

            "success": True,

            "summary": {
                "valid": True,
                "type": "international",
                "supported_region": False,
                "analysis_level": "generic",
                "risk_score": risk_score,
                "risk_level": (
                    "high"
                    if risk_score >= 70 else
                    "medium"
                    if risk_score >= 40 else
                    "low"
                ),
            },

            "risk": {
                "risk_score": risk_score,
                "risk_flags": risk_flags,
            },

            "features": features,
        })

        return response

    # ---------------------------------------------------
    # Base response
    # ---------------------------------------------------

    response = {
        "input": phone,

        "normalization": normalization,

        "classification": classification,
    }

    # ---------------------------------------------------
    # Hard failure
    # ---------------------------------------------------

    if not classification["is_valid"]:

        response.update({
            "success": False,
            "reason": "invalid_number"
        })

        return response

    # ---------------------------------------------------
    # Extract normalized local number
    # ---------------------------------------------------

    normalized = normalization["normalized"]

    digits = re.sub(r"\D", "", normalized)

    # Indian local mobile
    if classification["type"] == "indian_mobile":
        local = digits[-10:]

    else:
        local = digits

    # ---------------------------------------------------
    # Telecom lookup
    # ---------------------------------------------------

    carrier_data = lookup_prefix(local)

    # ---------------------------------------------------
    # Feature extraction
    # ---------------------------------------------------

    features = extract_features(
        local,
        carrier_data
    )

    # ---------------------------------------------------
    # Risk engine
    # ---------------------------------------------------

    risk_score, risk_flags = calculate_risk(
        features
    )

    # ---------------------------------------------------
    # Reachability estimation
    # ---------------------------------------------------

    reachability = estimate_reachability(
        features
    )

    # ---------------------------------------------------
    # WhatsApp estimation
    # ---------------------------------------------------

    whatsapp = estimate_whatsapp(
        features,
        reachability
    )

    # ---------------------------------------------------
    # Confidence aggregation
    # ---------------------------------------------------

    intelligence_confidence = round(
        (
            normalization["parse_confidence"]
            + reachability["reachability_confidence"]
            + whatsapp["whatsapp_confidence"]
        ) / 3,
        2
    )

    summary = {
        "valid": classification["is_valid"],

        "type": classification["type"],

        "carrier": carrier_data["carrier"],

        "circle": carrier_data["circle"],

        "risk_score": risk_score,

        "risk_level": (
            "high"
            if risk_score >= 70 else
            "medium"
            if risk_score >= 40 else
            "low"
        ),

        "reachability_probability":
            reachability["reachability_probability"],

        "reachability_level":
            reachability["reachability_level"],

        "whatsapp_probability":
            whatsapp["whatsapp_probability"],

        "whatsapp_likelihood":
            whatsapp["whatsapp_likelihood"],

        "overall_confidence":
            intelligence_confidence,
    }


    # ---------------------------------------------------
    # Final response
    # ---------------------------------------------------

    response.update({
        "summary": summary,

        "success": True,

        # ---------------------------------------------
        # Telecom intelligence
        # ---------------------------------------------

        "telecom": {
            "carrier": carrier_data["carrier"],
            "circle": carrier_data["circle"],
            "matched_prefix": carrier_data["matched_prefix"],
            "prefix_match_length": carrier_data["match_length"],
        },

        # ---------------------------------------------
        # Behavioral analysis
        # ---------------------------------------------

        "risk": {
            "risk_score": risk_score,
            "risk_flags": risk_flags,
        },

        # ---------------------------------------------
        # Reachability
        # ---------------------------------------------

        "reachability": reachability,

        # ---------------------------------------------
        # WhatsApp estimation
        # ---------------------------------------------

        "whatsapp": whatsapp,

        # ---------------------------------------------
        # Raw extracted features
        # ---------------------------------------------

        "features": features,

        # ---------------------------------------------
        # Overall confidence
        # ---------------------------------------------

        "intelligence_confidence": intelligence_confidence,
    })
    return response


# --- Example ---
if __name__ == "__main__":
    result = analyze_phone("+91 9876543210")
    print(json.dumps(result, indent=2))