/**

- Media Manipulation Filter - Core Algorithm
- Filters manipulative language from news headlines
  */

const manipulationMappings = {
violence_words: {
‘SLAMS’: ‘criticizes’,
‘DESTROYS’: ‘disagrees with’,
‘DEMOLISHES’: ‘responds to’,
‘BLASTS’: ‘comments on’,
‘RIPS’: ‘challenges’,
‘CRUSHES’: ‘opposes’,
‘ANNIHILATES’: ‘refutes’,
‘OBLITERATES’: ‘contradicts’,
‘EVISCERATES’: ‘analyzes critically’,
‘SLAUGHTERS’: ‘disputes’,
‘HAMMERS’: ‘criticizes’,
‘PUMMELS’: ‘debates’
},
crisis_amplification: {
‘DEVASTATING’: ‘significant’,
‘CATASTROPHIC’: ‘notable’,
‘EXPLOSIVE’: ‘unexpected’,
‘SHOCKING’: ‘surprising’,
‘STUNNING’: ‘noteworthy’,
‘JAW-DROPPING’: ‘interesting’,
‘MIND-BLOWING’: ‘unusual’,
‘EARTH-SHATTERING’: ‘important’,
‘BOMBSHELL’: ‘revelation’,
‘INCREDIBLE’: ‘notable’
},
urgency_manipulation: {
‘BREAKING:’: ‘’,
‘URGENT:’: ‘’,
‘ALERT:’: ‘’,
‘JUST IN:’: ‘’,
‘DEVELOPING:’: ‘’,
‘🚨’: ‘’,
‘⚠️’: ‘’
},
emotional_framing: {
‘REFUSES’: ‘declines’,
‘REJECTS’: ‘does not accept’,
‘DEMANDS’: ‘requests’,
‘ORDERS’: ‘directs’,
‘FORCES’: ‘requires’,
‘THREATENS’: ‘warns’,
‘ATTACKS’: ‘criticizes’,
‘DEFENDS’: ‘explains’,
‘BEGS’: ‘asks’,
‘PLEADS’: ‘requests’
},
economic_crisis: {
‘COLLAPSE’: ‘decrease’,
‘COLLAPSES’: ‘decreases’,
‘PLUMMET’: ‘fall’,
‘PLUMMETS’: ‘falls’,
‘SOAR’: ‘increase’,
‘SOARS’: ‘increases’,
‘SKYROCKET’: ‘rise’,
‘SKYROCKETS’: ‘rises’,
‘CRASH’: ‘drop’,
‘CRASHES’: ‘drops’,
‘TANK’: ‘decline’,
‘TANKS’: ‘declines’,
‘SURGE’: ‘grow’,
‘SURGES’: ‘grows’
}
};

class MediaFilter {
constructor() {
this.mappings = manipulationMappings;
this.allMappings = this.flattenMappings();
}

flattenMappings() {
const flat = {};
for (const category in this.mappings) {
Object.assign(flat, this.mappings[category]);
}
return flat;
}

/**

- Main filtering function
- @param {string} text - Original headline text
- @param {string} intensity - ‘light’, ‘medium’, or ‘heavy’
- @returns {object} Filtered result with metadata
  */
  filter(text, intensity = ‘medium’) {
  const result = {
  original: text,
  filtered: text,
  manipulationFound: [],
  categories: new Set(),
  intensity: intensity
  };

```
// Apply filters based on intensity
const categoriesToApply = this.getCategoriesToApply(intensity);

for (const category of categoriesToApply) {
  const categoryMappings = this.mappings[category];
  
  for (const [manipulative, neutral] of Object.entries(categoryMappings)) {
    // Case-insensitive search, but preserve original case in replacement
    const regex = new RegExp(`\\b${this.escapeRegex(manipulative)}\\b`, 'gi');
    
    if (regex.test(result.filtered)) {
      result.manipulationFound.push({
        word: manipulative,
        replacement: neutral,
        category: category
      });
      result.categories.add(category);
      
      // Replace with neutral term
      result.filtered = result.filtered.replace(regex, neutral);
    }
  }
}

// Clean up extra spaces and formatting
result.filtered = this.cleanText(result.filtered);
result.categories = Array.from(result.categories);

return result;
```

}

getCategoriesToApply(intensity) {
switch(intensity) {
case ‘light’:
return [‘violence_words’, ‘urgency_manipulation’];
case ‘medium’:
return [‘violence_words’, ‘urgency_manipulation’, ‘crisis_amplification’, ‘emotional_framing’];
case ‘heavy’:
return Object.keys(this.mappings);
default:
return [‘violence_words’, ‘urgency_manipulation’, ‘crisis_amplification’];
}
}

cleanText(text) {
return text
.replace(/\s+/g, ’ ’)  // Remove extra spaces
.replace(/\s([,.!?])/g, ‘$1’)  // Fix punctuation spacing
.trim();
}

escapeRegex(str) {
return str.replace(/[.*+?^${}()|[]\]/g, ‘\$&’);
}

/**

- Analyze text without filtering
- @param {string} text - Text to analyze
- @returns {object} Analysis results
  */
  analyze(text) {
  const analysis = {
  original: text,
  manipulationScore: 0,
  foundWords: [],
  categories: {}
  };

```
for (const [category, mappings] of Object.entries(this.mappings)) {
  analysis.categories[category] = [];
  
  for (const manipulative of Object.keys(mappings)) {
    const regex = new RegExp(`\\b${this.escapeRegex(manipulative)}\\b`, 'gi');
    const matches = text.match(regex);
    
    if (matches) {
      analysis.foundWords.push(manipulative);
      analysis.categories[category].push(manipulative);
      analysis.manipulationScore += matches.length;
    }
  }
}

return analysis;
```

}

/**

- Get suggested missing context questions
- @param {string} text - Original headline
- @returns {array} Array of context questions
  */
  getMissingContext(text) {
  const questions = [];

```
// Check for economic claims
if (/price|cost|market|economy/i.test(text)) {
  questions.push("What percentage change actually occurred?");
  questions.push("What was the baseline or previous value?");
  questions.push("Is this change within normal market fluctuation?");
}

// Check for conflict language
if (/attack|war|fight|battle|conflict/i.test(text)) {
  questions.push("What events preceded this action?");
  questions.push("What was the stated reason for this decision?");
  questions.push("Are there competing perspectives on what happened?");
}

// Check for political claims
if (/trump|biden|congress|senate|president/i.test(text)) {
  questions.push("What was the full statement or policy?");
  questions.push("What context is being omitted?");
  questions.push("How did fact-checkers assess this claim?");
}

// Check for absolute claims
if (/refuse|never|always|completely|totally/i.test(text)) {
  questions.push("Is this an absolute statement or are there exceptions?");
  questions.push("What nuance is being removed?");
}

// General questions
questions.push("Who benefits from this framing?");
questions.push("What information might challenge this narrative?");

return questions;
```

}
}

// Export for use in browser or Node.js
if (typeof module !== ‘undefined’ && module.exports) {
module.exports = MediaFilter;
}
