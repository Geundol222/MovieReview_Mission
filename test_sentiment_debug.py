"""Debug script to test sentiment analysis with new model."""
from backend.sentiment import analyze, _get_labels
import sys

# Test cases with clear sentiment
test_cases = [
    ("이 영화 정말 최고예요! 너무 재밌어요!", "positive"),  # Clear positive
    ("최악의 영화. 시간 낭비했어요.", "negative"),  # Clear negative
    ("간만에 몸이 비비 꼬였네요. 너무 기대한듯.", "negative"),  # Your example - negative
    ("영화 연출과 감정 묘사 최고의 몰입감입니다", "positive"),  # Positive
    ("무려 세시간동안 증언하고 조사받는 얘기. 잠 고문받을 것.", "negative"),  # From your data - negative
]

print("=" * 80)
print(f"Model: sangrimlee/bert-base-multilingual-cased-nsmc")
print(f"Labels: {_get_labels()}")
print("=" * 80)

all_correct = True
for text, expected in test_cases:
    score, label = analyze(text)
    is_correct = label == expected
    status = "✓" if is_correct else "✗"

    if not is_correct:
        all_correct = False

    print(f"\n{status} Text: {text}")
    print(f"  Expected: {expected} | Got: {label} (score: {score:.3f})")

print("\n" + "=" * 80)
if all_correct:
    print("All tests passed!")
    sys.exit(0)
else:
    print("Some tests failed!")
    sys.exit(1)
