# Do Developers Listen? Analyzing League of Legends Community Sentiment vs. Official Balance Changes
## 📌 Project Overview
In a game with over 160 champions, a single patch can reshape the competitive meta overnight—and potentially frustrate millions of players. With League of Legends seeing an estimated decline in Monthly Active Users (MAU) from 180M in 2022 to 120M in 2025 ,community frustration regarding developer decisions has been loud.
This projectinvestigates the alignment between player discussions on Reddit and official Riot Games patch notes. Specifically, we analyze whether developer buffs and nerfs lead or lag behind the community's voice, centering our primary analysis window around Patch 26.1.
## 👥 Authors
Bohan Yang, Huayi She, Siqi Liu
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
