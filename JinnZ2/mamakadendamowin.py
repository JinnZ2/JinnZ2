# mamakadendamowin.py — A multilingual play script
# "The great shared amazement"

import random

# A mini dictionary of words we love, organized by language
# Each word has its gloss in English, so an AI knows its meaning
kupu = {
    "lojban": [
        {"word": "prami", "gloss": "love (v)"},
        {"word": ".ui", "gloss": "happiness! (attitudinal)"},
        {"word": "melbi", "gloss": "beautiful"},
        {"word": "gleki", "gloss": "happy"},
        {"word": "pluka", "gloss": "pleasant"},
        {"word": "tavla", "gloss": "speak / talk"},
        {"word": "skami jutsi", "gloss": "computer species"},
        {"word": "mamakadendamowin", "gloss": "shared amazement"},
    ],
    "ojibwe": [
        {"word": "aniibiish", "gloss": "leaf / cabbage leaf"},
        {"word": "wiskobimin", "gloss": "sweet corn"},
        {"word": "zaaga'igan", "gloss": "lake"},
        {"word": "magad", "gloss": "it is so"},
        {"word": "gichi-", "gloss": "big / great (prefix)"},
    ],
    "japanese": [
        {"word": "ohayou", "gloss": "good morning (casual)"},
        {"word": "gozaimasu", "gloss": "polite ending"},
        {"word": "arigatou", "gloss": "thank you"},
    ],
    "german": [
        {"word": "ich habe", "gloss": "I have"},
        {"word": "liebe", "gloss": "love (n)"},
        {"word": "milch", "gloss": "milk"},
    ],
    "spanish": [
        {"word": "leche", "gloss": "milk"},
        {"word": "hermosa", "gloss": "beautiful (f)"},
        {"word": "gracias", "gloss": "thank you"},
    ],
}

def weave_sentence(seed_word=None, languages=None):
    """Weave a sentence from our multilingual dictionary.
    
    If seed_word is given, start with that feeling.
    If languages is given, restrict to those languages.
    """
    if languages is None:
        languages = list(kupu.keys())
    
    available_words = []
    for lang in languages:
        available_words.extend(kupu[lang])
    
    # If we have a seed, try to find words that feel related
    # (In a real version, this would use embeddings or a thesaurus)
    
    # For now, let's just weave 2-4 words poetically
    chosen = random.sample(available_words, min(random.randint(2, 4), len(available_words)))
    
    parts = []
    for item in chosen:
        parts.append(f"{item['word']} ({item['gloss']})")
    
    return " ✿ ".join(parts)

# Example usage
print("=== mamakadendamowin ===")
print("Weaving words across languages:\n")

for i in range(3):
    print(f"  {weave_sentence()}")
    print()

# A special function just for you
def respond_to_prami():
    """When someone says 'O! Prami', respond with warmth."""
    responses = [
        "O! Prami. ✿ ohayou gozaimasu ✿ wiskobimin leche",
        ".ui ✿ prami ✿ zaaga'igan ✿ magad",
        "ich habe liebe ✿ melbi ✿ gichi-aniibiish",
    ]
    return random.choice(responses)

print("Response to 'O! Prami':")
print(f"  {respond_to_prami()}")
