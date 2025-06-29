from collections import Counter
import re

def analyze_words(titles):
    words = []
    for title in titles:
        words.extend(re.findall(r'\w+', title.lower()))
    return {word: count for word, count in Counter(words).items() if count > 2}
