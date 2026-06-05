"""
Use an LLM to classify each champion's balance direction for Patch 26.1.

Input: lol_patch_notes_champion_updates_categorized.csv under the repository root.
Output: analysis_output_v3/patch_26_1_direction.csv (champion, direction, confidence, reasoning).
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv
from tqdm import tqdm


load_dotenv()



_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
ANALYSIS_OUTPUT_V3 = _SCRIPT_DIR / "analysis_output_v3"
ANALYSIS_OUTPUT_V3.mkdir(parents=True, exist_ok=True)

INPUT_CSV = str(_REPO_ROOT / "lol_patch_notes_champion_updates_categorized.csv")
OUTPUT_CSV = str(ANALYSIS_OUTPUT_V3 / "patch_26_1_direction.csv")
CHECKPOINT_PATH = str(ANALYSIS_OUTPUT_V3 / "patch_direction_checkpoint.json")

TARGET_PATCH = "26.1"  # Only process Patch 26.1
MODEL = "claude-haiku-4-5-20251001"


SYSTEM_PROMPT = """You are an expert on League of Legends balance changes.

You understand that whether a change is a buff or nerf depends on the stat's meaning:
- Higher damage, ratios, shields, heals = buff
- Lower cooldowns, mana costs = buff
- Higher CC duration, range = buff
- Lower damage, ratios = nerf
- Higher cooldowns, mana costs = nerf

Respond ONLY with a JSON object, no other text."""


USER_PROMPT_TEMPLATE = """Champion: {champion}
Patch: {patch_title}
Changes:
{changes}

Task: Classify the overall direction of these changes for {champion}.

Categories:
- BUFF: Overall makes the champion stronger
- NERF: Overall makes the champion weaker
- MIXED: Contains meaningful buffs AND nerfs, roughly balanced
- REWORK: Significant mechanical changes that alter how the champion plays (regardless of power)
- ADJUSTMENT: Minor tweaks where direction is unclear or negligible

Respond with ONLY this JSON:
{{"direction": "BUFF|NERF|MIXED|REWORK|ADJUSTMENT", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""


def classify_patch(client: Anthropic, champion: str, patch_title: str, changes: str) -> Dict:
    prompt = USER_PROMPT_TEMPLATE.format(
        champion=champion,
        patch_title=patch_title,
        changes=changes[:2000],  # Truncate very long change text
    )
    
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    
    raw = response.content[0].text.strip()
    
    try:
        start = raw.find("{")
        end = raw.rfind("}")
        result = json.loads(raw[start:end + 1])
    except Exception as e:
        result = {
            "direction": "PARSE_ERROR",
            "confidence": 0.0,
            "reasoning": f"Parse failed: {e}",
        }
    
    result["_input_tokens"] = response.usage.input_tokens
    result["_output_tokens"] = response.usage.output_tokens
    return result


def load_checkpoint() -> Dict:
    if Path(CHECKPOINT_PATH).exists():
        with open(CHECKPOINT_PATH, "r") as f:
            return json.load(f)
    return {}


def save_checkpoint(cp: Dict):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(cp, f)


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    
    client = Anthropic(api_key=api_key)
    
    df = pd.read_csv(INPUT_CSV)
    
    # Filter to Patch 26.1 only (exclude 26.10, 26.11, etc.)
    mask = df['patch_title'].str.contains(r'26\.1', na=False, regex=True)
    mask &= ~df['patch_title'].str.contains(r'26\.1[0-9]', na=False, regex=True)
    df = df[mask].reset_index(drop=True)
    
    print(f"Processing {len(df)} champions from patch 26.1")
    
    checkpoint = load_checkpoint()
    results = []
    total_in = 0
    total_out = 0
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Classifying patches"):
        champion = row['champion']
        
        if champion in checkpoint:
            results.append(checkpoint[champion])
            continue
        
        try:
            result = classify_patch(
                client,
                champion=champion,
                patch_title=row['patch_title'],
                changes=str(row['champion_update']),
            )
            result['champion'] = champion
            result['patch_title'] = row['patch_title']
            result['raw_changes'] = str(row['champion_update'])[:500]  # First 500 chars for review
            
            checkpoint[champion] = result
            results.append(result)
            total_in += result.get('_input_tokens', 0)
            total_out += result.get('_output_tokens', 0)
            
            save_checkpoint(checkpoint)  # Save after each row (small checkpoint size)
            time.sleep(0.1)
            
        except Exception as e:
            print(f"\n! Error on {champion}: {e}")
            results.append({
                'champion': champion,
                'direction': 'API_ERROR',
                'confidence': 0,
                'reasoning': str(e)[:200],
            })
    
    result_df = pd.DataFrame(results)
    out_cols = ['champion', 'patch_title', 'direction', 'confidence', 'reasoning', 'raw_changes']
    result_df = result_df[[c for c in out_cols if c in result_df.columns]]
    result_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    
    print(f"\n✓ Saved to {OUTPUT_CSV}")
    print("\n=== Direction Distribution ===")
    print(result_df['direction'].value_counts())
    
    cost = total_in * 0.8 / 1_000_000 + total_out * 4 / 1_000_000
    print(f"\nCost: ${cost:.4f}")


if __name__ == "__main__":
    main()