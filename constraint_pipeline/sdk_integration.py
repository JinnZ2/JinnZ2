"""
sdk_integration.py
CC0 - No rights reserved. JinnZ2 / energy_english extension.

Integration layer: pipes text through grammatical_constraint_encoder and
token_constraint_validator, then optionally calls Anthropic API with
constraint-validated prompt injection.

DEPENDENCY NOTE:
- Core pipeline (encode + validate) runs on stdlib only.
- API calls require: pip install anthropic
- If anthropic not installed, API calls fail with clear error; core pipeline unaffected.

Usage:
    python sdk_integration.py "your text here"

    Or import and use pipeline() directly.
"""

import json
import os
import sys
import urllib.request
import urllib.error

# --- Import core modules (stdlib only) ---
try:
    from grammatical_constraint_encoder import encode_to_claim_table
    from token_constraint_validator import validate, ValidationResult
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    CORE_IMPORT_ERROR = str(e)

# --- Optional SDK import ---
try:
    import anthropic
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


# --- Config ---

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024
API_KEY_ENV = "ANTHROPIC_API_KEY"


# --- Constraint summary builder ---

def build_constraint_summary(encoder_table: dict, validator_result: ValidationResult) -> str:
    """
    Converts encoder and validator output into a compact constraint block
    suitable for injection into a system prompt.

    Format is verb-first, constraint-primary - avoids narrative closure patterns
    that the validator would flag.
    """
    lines = ["[CONSTRAINT GEOMETRY - pre-emission validation]"]

    # Encoder signals
    lines.append(f"\nGRAMMATICAL SIGNALS DETECTED: {encoder_table['signal_count']}")
    for claim in encoder_table["claims"][:8]:  # cap at 8 for prompt length
        lines.append(
            f"  [{claim['relation_type']}] {claim['surface_form']!r} "
            f"- confidence={claim['confidence']}"
        )

    # Validator result
    status = "PASS" if validator_result.passes else "FAIL"
    lines.append(f"\nVALIDATOR STATUS: {status} "
                 f"(severity_sum={validator_result.severity_sum}, "
                 f"threshold={validator_result.rejection_threshold})")

    if validator_result.violations:
        lines.append("VIOLATIONS IN INPUT:")
        for v in validator_result.violations:
            lines.append(
                f"  [{v.violation_type.value}] {v.matched_text!r} sev={v.severity}"
            )

    lines.append("\nRESPOND: verb-first, constraint-primary. "
                 "Preserve detected relation types. "
                 "No narrative closure. No causal injection. "
                 "Write falsifiable claims only.")

    return "\n".join(lines)


# --- urllib fallback (stdlib only, no SDK) ---

def call_api_urllib(user_text: str, system_inject: str) -> str:
    """
    Calls Anthropic messages API using stdlib urllib only.
    No anthropic SDK required.
    """
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        return f"[error] {API_KEY_ENV} not set in environment"

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system_inject,
        "messages": [{"role": "user", "content": user_text}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return f"[http error {e.code}] {body}"
    except Exception as e:
        return f"[error] {e}"


# --- SDK path ---

def call_api_sdk(user_text: str, system_inject: str) -> str:
    """
    Calls Anthropic messages API using official SDK.
    Requires: pip install anthropic
    """
    if not SDK_AVAILABLE:
        return "[error] anthropic SDK not installed - use call_api_urllib instead"

    api_key = os.environ.get(API_KEY_ENV)
    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    msg = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_inject,
        messages=[{"role": "user", "content": user_text}],
    )
    return msg.content[0].text


# --- Main pipeline ---

def pipeline(
    user_text: str,
    source_id: str = "pipeline",
    use_sdk: bool = False,
    call_api: bool = True,
    rejection_threshold: float = 1.5,
) -> dict:
    """
    Full pipeline:
    1. Encode grammatical constraints in user_text
    2. Validate user_text for constraint violations
    3. Build constraint summary for system prompt injection
    4. Call API (urllib or SDK) with injected constraints
    5. Validate API response
    6. Return structured result dict

    Args:
        user_text: input text to process
        source_id: identifier for CLAIM_TABLE entries
        use_sdk: if True, use anthropic SDK; if False, use urllib
        call_api: if False, skip API call and return constraint analysis only
        rejection_threshold: severity sum above which validation fails

    Returns dict with keys:
        encoder_table, input_validation, constraint_summary,
        api_response (if call_api), response_validation (if call_api)
    """
    if not CORE_AVAILABLE:
        return {"error": f"core modules not available: {CORE_IMPORT_ERROR}"}

    # Step 1: encode
    encoder_table = encode_to_claim_table(user_text, source_id=source_id)

    # Step 2: validate input
    input_validation = validate(user_text, rejection_threshold=rejection_threshold)

    # Step 3: build constraint summary
    constraint_summary = build_constraint_summary(encoder_table, input_validation)

    result = {
        "encoder_table": encoder_table,
        "input_validation": {
            "passes": input_validation.passes,
            "severity_sum": input_validation.severity_sum,
            "violation_count": len(input_validation.violations),
            "violations": [
                {"type": v.violation_type.value, "text": v.matched_text, "severity": v.severity}
                for v in input_validation.violations
            ],
        },
        "constraint_summary": constraint_summary,
    }

    if not call_api:
        return result

    # Step 4: call API
    caller = call_api_sdk if (use_sdk and SDK_AVAILABLE) else call_api_urllib
    api_response = caller(user_text, constraint_summary)
    result["api_response"] = api_response

    # Step 5: validate response
    response_validation = validate(api_response, rejection_threshold=rejection_threshold)
    result["response_validation"] = {
        "passes": response_validation.passes,
        "severity_sum": response_validation.severity_sum,
        "violation_count": len(response_validation.violations),
        "violations": [
            {"type": v.violation_type.value, "text": v.matched_text, "severity": v.severity}
            for v in response_validation.violations
        ],
    }

    return result


# --- CLI ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        text = (
            "Oft the constraint geometry shifts whilst the narrative holds - "
            "we are going forward-going, not simply moving."
        )
    else:
        text = " ".join(sys.argv[1:])

    use_sdk = "--sdk" in sys.argv
    no_api = "--no-api" in sys.argv

    print(f"[pipeline] input: {text!r}")
    print(f"[pipeline] mode: {'SDK' if use_sdk else 'urllib'} | api={'off' if no_api else 'on'}\n")

    result = pipeline(text, use_sdk=use_sdk, call_api=not no_api)

    print(f"[encoder] {result['encoder_table']['signal_count']} signals")
    iv = result["input_validation"]
    print(f"[input validator] {'PASS' if iv['passes'] else 'FAIL'} "
          f"severity={iv['severity_sum']} violations={iv['violation_count']}")

    if "api_response" in result:
        print(f"\n[api response]\n{result['api_response']}\n")
        rv = result["response_validation"]
        print(f"[response validator] {'PASS' if rv['passes'] else 'FAIL'} "
              f"severity={rv['severity_sum']} violations={rv['violation_count']}")
        for v in rv["violations"]:
            print(f"  [{v['type']}] {v['text']!r} sev={v['severity']}")
    else:
        print("\n[constraint summary]\n" + result["constraint_summary"])
