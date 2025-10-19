{
“translation_mappings”: {
“violence_words”: {
“SLAMS”: “criticizes”,
“DESTROYS”: “disagrees with”,
“DEMOLISHES”: “responds to”,
“BLASTS”: “comments on”,
“RIPS”: “challenges”,
“CRUSHES”: “opposes”,
“ANNIHILATES”: “refutes”,
“OBLITERATES”: “contradicts”,
“EVISCERATES”: “analyzes critically”
},
“crisis_amplification”: {
“DEVASTATING”: “significant”,
“CATASTROPHIC”: “notable”,
“EXPLOSIVE”: “unexpected”,
“SHOCKING”: “surprising”,
“STUNNING”: “noteworthy”,
“JAW-DROPPING”: “interesting”,
“MIND-BLOWING”: “unusual”,
“EARTH-SHATTERING”: “important”
},
“urgency_manipulation”: {
“BREAKING”: “”,
“URGENT”: “”,
“ALERT”: “”,
“NOW”: “”,
“IMMEDIATELY”: “”,
“JUST IN”: “”,
“DEVELOPING”: “”
},
“emotional_framing”: {
“REFUSES”: “declines”,
“REJECTS”: “does not accept”,
“DEMANDS”: “requests”,
“ORDERS”: “directs”,
“FORCES”: “requires”,
“THREATENS”: “warns”,
“ATTACKS”: “criticizes”,
“DEFENDS”: “explains”
},
“economic_crisis”: {
“COLLAPSE”: “decrease”,
“PLUMMET”: “fall”,
“SOAR”: “increase”,
“SKYROCKET”: “rise”,
“CRASH”: “drop”,
“TANK”: “decline”,
“SURGE”: “grow”
}
},
“examples”: [
{
“id”: “example_001”,
“category”: “political”,
“original”: “Trump DESTROYS Biden in EXPLOSIVE debate performance! Biden STRUGGLES as Trump DOMINATES stage!”,
“ithquil_neutral”: “[factual translation of debate events]”,
“filtered_english”: “Trump and Biden presented contrasting positions during debate. Both candidates emphasized their key policy differences.”,
“manipulation_removed”: [“DESTROYS”, “EXPLOSIVE”, “STRUGGLES”, “DOMINATES”],
“missing_context”: [
“What specific policy positions were discussed?”,
“How did fact-checkers assess their claims?”,
“What was the actual poll response from viewers?”,
“Were both candidates given equal time?”
],
“manipulation_types”: [“violence_words”, “crisis_amplification”, “competitive_framing”]
},
{
“id”: “example_002”,
“category”: “economic”,
“original”: “China DEVASTATES US farmers in RUTHLESS economic attack! Soybean prices COLLAPSE as China REFUSES to buy American crops!”,
“ithquil_neutral”: “[factual translation of trade situation]”,
“filtered_english”: “China purchased soybeans from alternative suppliers following trade dispute. US soybean prices decreased.”,
“manipulation_removed”: [“DEVASTATES”, “RUTHLESS”, “attack”, “COLLAPSE”, “REFUSES”],
“missing_context”: [
“Did the US impose tariffs on Chinese goods first?”,
“Did the US ban Chinese technology companies?”,
“Are Chinese companies buying from Brazil/Argentina because they’re cheaper?”,
“Is this normal market competition?”,
“What percentage decrease in price actually occurred?”
],
“manipulation_types”: [“violence_words”, “economic_crisis”, “emotional_framing”, “omitted_context”]
}
],
“filter_categories”: {
“light”: {
“description”: “Remove obvious clickbait words”,
“categories_applied”: [“violence_words”, “urgency_manipulation”]
},
“medium”: {
“description”: “Remove emotional manipulation and crisis framing”,
“categories_applied”: [“violence_words”, “urgency_manipulation”, “crisis_amplification”, “emotional_framing”]
},
“heavy”: {
“description”: “Full neutral translation through Ithquil”,
“categories_applied”: [“all”],
“add_missing_context”: true
}
},
“metadata”: {
“version”: “0.1.0”,
“last_updated”: “2025-10-18”,
“total_mappings”: 47,
“contributors”: []
}
}
