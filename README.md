# Do Developers Listen? Analyzing League of Legends Community Sentiment vs. Official Balance Changes
## 📌 Project Overview
In a game with over 160 champions, a single patch can reshape the competitive meta overnight—and potentially frustrate millions of players. With League of Legends seeing an estimated decline in Monthly Active Users (MAU) from 180M in 2022 to 120M in 2025 ,community frustration regarding developer decisions has been loud.
This projectinvestigates the alignment between player discussions on Reddit and official Riot Games patch notes. Specifically, we analyze whether developer buffs and nerfs lead or lag behind the community's voice, centering our primary analysis window around Patch 26.1.
## 👥 Authors
Bohan Yang, Huayi She, Siqi Liu
## 🎯Project Object
This study examines whether community sentiment on Reddit aligns with Riot Games' official balance decisions in League of Legends, and whether community discussion functions as a leading or lagging signal relative to official patches. We focus on Patch 26.1, the major content update opening Season 1 of 2026, which adjusted 34 champions amid system-wide changes including a critical-strike damage rework.
The research addresses two questions of broad interest. Academically, it asks whether platform-based sentiment analysis reliably captures community opinion in domains with skewed engagement distributions, as this method is widely used in marketing, political science, and product research. Commercially, it asks how a live-service product team should weight community discussion when calibrating product decisions: as a forward-looking input, a backward-looking diagnostic, or neither.
## 🛠 Methodology & Architecture
Our architecture consists of three converging data pipelines:
### 1. Patch Pipeline (Riot's Intent)
Data Collection: Scraped official patch notes directly from the League of Legends website.
Parsing: Extracted 163 patches and 2,540 champion-level changes into a queryable dataset.
LLM Labeling: Utilized Claude Haiku to classify each patch's intent into direction labels: BUFF, NERF, MIXED, or REWORK.
### 2. Champion Alias Resolver (Name Normalization)
Players rarely use official champion names (e.g., typing "mf" instead of "Miss Fortune"). To bridge community data and official data, we built a robust resolver:
Merged the official Riot Data Dragon API (170 champions) with a custom community slang dictionary (~50 nicknames).
Generated a normalized lookup table with roughly 1,500 alias-to-canonical-name mappings.
### 3. Reddit Pipeline (Player Reactions)
Data Collection: Scraped r/leagueoflegends via the Reddit API.
Filtering Funnel: Narrowed down hundreds of daily posts by filtering for champions changed in Patch 26.1, expanding search queries via our Alias Resolver, and restricting to a 4-week window (±2 weeks around release).
Sentiment Labeling: Applied Claude Haiku to classify player stance into: TOO_STRONG, TOO_WEAK, MECHANICAL_ISSUE, NEUTRAL_DISCUSSION, or NOT_ABOUT_CHAMPION
# 📊 Key Findings
1. Players demand heavier nerfs: Among posts discussing nerfed champions, complaints that the champion was "still too strong" (37%) were 5.4x more common than complaints that they were "nerfed too hard" (7%).
2. Reaction by Developer Intent: TOO_STRONG sentiments dominated both the NERF and MIXED patches, indicating players default to demanding more nerfs. Meaningful TOO_WEAK complaints (29%) were primarily triggered only when a champion received a BUFF.
3. Most Controversial Champions: Smolder and Shaco showed the strongest "still too strong" signal in the dataset. Champions like Nilah and Draven had 75% of their relevant posts claiming they were too strong.
4. Temporal Shifts: Post volume spiked the day after the patch release. Furthermore, TOO_WEAK ("nerfed too hard") complaints only appeared after the patch went live, as players reacted to experienced changes.
# 📂 Repository Structure
patch_scraper.ipynb: Scripts to scrape and parse Riot patch notes.  
champion_aliases.py: Builds the in-memory name resolver utilizing Data Dragon.
reddit_scraper_v2.py: Fetches Reddit posts based on champion filters.  
llm_patch_direction.py: Prompts Claude Haiku for buff/nerf classification.  
llm_sentiment.py: Classifies Reddit post stances.
alignment_analysis_v3.py: Final statistical tests (Mann-Whitney U, Chi-square), event studies, and chart generation.  
# ⚠️ Limitations
1. Scope: The analysis was restricted to a single patch window (Patch 26.1) and may not generalize across different metas.
2. Variables: Item and system changes (runes) were ignored, which also shape champion strength.
3. Data Depth: We analyzed post titles and body text (selftext), but comment threads were excluded, potentially missing nuanced opinions.
4. Platform Bias: Data is exclusively from Reddit, excluding other massive player bases (e.g., Weibo, X/Twitter, official forums).
