"""Write the teaching passages for the corpus-extension experiment into corpus/.

Four of the eval suite's extension skills get one file each: grammar, opposites,
negation, and reference. Every passage is generated here from word lists and
sentence frames, the same way the notebook builds its classroom corpus, so this
script is the source. Stories that span sentences are written with no space after
the internal periods, because the notebook splits passages at a period followed by
whitespace. The tokenizer still separates the periods, so the model sees
"the cup is not white . it is black . the cup is black ." as one passage.

Nothing here copies a test item. Beyond the notebook's own check, which rejects an
imported file containing an exact prompt, this script refuses to write a line that
contains an eval prompt or the first sentence of an eval story, never pairs the
three test couples (maya and leo, ella and finn, omar and nina), and never puts a
test subject with either of its test items (ava with tea or milk, the box with red
or blue, the door with open or closed). Those words still appear in other stories.

Usage: .venv/bin/python scripts/make_teaching_corpus.py [output folder, default corpus]
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from run_evals import load_suite, matching_cases, normalized  # noqa: E402

SUITE = load_suite(ROOT / "evals/language_evals.json")
PROMPTS = {normalized(case["prompt"]) for case in SUITE["cases"]}
FIRST_SENTENCES = {normalized(case["prompt"].split(" . ")[0]) for case in SUITE["cases"]}
TEST_STORY_WORDS = {"box": {"red", "blue"}, "door": {"open", "closed"}, "ava": {"tea", "milk"}}
TEST_PAIRS = [{"maya", "leo"}, {"ella", "finn"}, {"omar", "nina"}]

PLACES = "store market bank kitchen station office hospital school park beach farm library".split()
NAMES = {"maya": "she", "leo": "he", "nora": "she", "omar": "he", "ella": "she", "finn": "he",
         "sara": "she", "noah": "he", "nina": "she", "emma": "she", "luca": "he", "ava": "she",
         "mia": "she", "eli": "he", "zoe": "she", "ivan": "he", "rosa": "she", "theo": "he",
         "lily": "she", "hugo": "he"}


def grammar(rng):
    animals = "bird cat dog cow horse duck goat frog rabbit pig hen lamb".split()
    adjectives = ("hungry tired happy quiet loud ready late early small big wet dry warm cold "
                  "asleep awake calm busy clean dirty").split()
    verbs = "walk talk play work wait cook clean jump look rest listen laugh".split()
    lines = []
    for animal in animals:  # agreement: every animal with four adjectives in every frame
        for adj in rng.sample(adjectives, 4):
            lines += [f"the {animal} is {adj} .", f"a {animal} is {adj} .",
                      f"two {animal}s are {adj} .", f"many {animal}s are {adj} ."]
            if animal != "bird":  # "one bird" is a test prompt
                lines += [f"one {animal} is {adj} .", f"one {animal} was {adj} yesterday ."]
            if animal != "dog":  # "the dogs" is a test prompt
                lines += [f"the {animal}s are {adj} .", f"the {animal}s were {adj} yesterday ."]
    for adj in adjectives:  # pronouns with am, is, are, was, were
        lines += [f"i am {adj} today .", f"we are {adj} today .", f"he is {adj} today .",
                  f"she is {adj} today .", f"they were {adj} yesterday .", f"he was {adj} yesterday ."]
    for verb in verbs:  # tense: every verb in its past, third-person, and -ing forms
        past, third, ing = verb + "ed", verb + "s", verb + "ing"
        for place in rng.sample(PLACES, 3):
            subject = rng.choice(["he", "they", "we", "i", "the teacher", "the nurse", "the driver"])
            lines.append(f"yesterday {subject} {past} at the {place} .")  # never "yesterday she"
            lines += [f"she {past} at the {place} yesterday .", f"last week he {past} to the {place} .",
                      f"today she {third} at the {place} .", f"every day he {third} to the {place} .",
                      f"she is {ing} at the {place} now .", f"they are {ing} at the {place} now .",
                      f"every day they {verb} to the {place} .", f"today we {verb} at the {place} ."]
    return lines


def opposites(rng):
    pairs = [("hot", "cold"), ("empty", "full"), ("noisy", "quiet"), ("loud", "quiet"),
             ("fast", "slow"), ("heavy", "light"), ("early", "late"), ("soft", "hard"),
             ("warm", "cool"), ("round", "square"), ("big", "small"), ("tall", "short"),
             ("wet", "dry"), ("open", "closed"), ("clean", "dirty"), ("old", "new"),
             ("high", "low"), ("dark", "bright"), ("long", "short"), ("thick", "thin"),
             ("sweet", "sour"), ("rich", "poor"), ("young", "old"), ("strong", "weak")]
    nouns = "soup tea coffee water room street box bag cup road house car song voice bread stone pillow bell path hill".split()
    lines = []
    for first, second in pairs:
        for a, b in [(first, second), (second, first)]:
            if normalized(f"the opposite of {a} is") not in PROMPTS:
                lines.append(f"the opposite of {a} is {b} .")
            lines += [f"{a} is the opposite of {b} .", f"{a} and {b} are opposites .", f"{a} means not {b} ."]
            for noun in rng.sample(nouns, 3):
                other = rng.choice([n for n in nouns if n != noun])
                lines.append(rng.choice([f"the {noun} was {a} but the {other} was {b} .",
                                         f"if the {noun} is not {a} then it is {b} .",
                                         f"a {noun} can be {a} or {b} .",
                                         f"when the {noun} is {a} it is not {b} ."]))
    return lines


def negation(rng):
    objects = "box cup hat bag car door wall book ball shirt chair lamp coat bike boat house window gate key road".split()
    colors = "red blue green yellow white black brown pink gray purple".split()
    states = [("open", "closed"), ("full", "empty"), ("hot", "cold"), ("clean", "dirty"), ("wet", "dry"),
              ("big", "small"), ("new", "old"), ("heavy", "light"), ("narrow", "wide"), ("here", "missing"),
              ("broken", "fixed"), ("locked", "unlocked")]
    foods = "tea milk rice bread coffee water soup cake cheese eggs apples pears juice butter honey salt beans corn fish meat".split()
    verbs = [("buy", "bought"), ("order", "ordered"), ("want", "wanted"), ("choose", "chose"), ("bring", "brought"),
             ("take", "took"), ("eat", "ate"), ("drink", "drank"), ("pick", "picked"), ("get", "got")]
    object_frames = ["the {obj} is not {a}.it is {b}.the {obj} is {b}.",
                     "the {obj} is not {a}.it is {b}.so the {obj} is {b}.",
                     "the {obj} was not {a}.it was {b}.the {obj} was {b}.",
                     "this {obj} is not {a}.it is {b}.this {obj} is {b}.",
                     "my {obj} is not {a}.it is {b}.my {obj} is {b}."]
    person_frames = ["{name} did not {verb} {x}.{pron} {past} {y}.{name} {past} {y}.",
                     "{name} did not {verb} the {x}.{pron} {past} the {y}.{name} {past} the {y}.",
                     "{name} did not {verb} {x}.{pron} {past} {y} instead.{name} {past} {y}."]
    contrasts = [(a, b) for a in colors for b in colors if a != b] + [p for s in states for p in (s, s[::-1])]
    lines = []
    for a, b in contrasts:  # every contrast on three objects, so every color and state gets taught
        for obj in rng.sample([o for o in objects if not {a, b} & TEST_STORY_WORDS.get(o, set())], 3):
            lines.append(rng.choice(object_frames).format(obj=obj, a=a, b=b))
    for name, pron in NAMES.items():  # every person with five verbs and two food pairs each
        allowed = [f for f in foods if f not in TEST_STORY_WORDS.get(name, set())]
        for verb, past in rng.sample(verbs, 5):
            for _ in range(2):
                x, y = rng.sample(allowed, 2)
                lines.append(rng.choice(person_frames).format(name=name, pron=pron, verb=verb, past=past, x=x, y=y))
    return lines


def reference(rng):
    objects = "book pencil lamp cup hat bag ball key coin letter map ring note toy pen card gift coat brush phone".split()
    gift_frames = ["{a} lent a {obj} to {b}.{b} thanked {a}.",
                   "{a} gave {b} a {obj}.{b} thanked {a}.",
                   "{a} handed a {obj} to {b}.{b} thanked {a}.",
                   "{a} sent a {obj} to {b}.{b} thanked {a}.",
                   "{a} gave {b} a {obj}.the person who received the {obj} was {b}.",
                   "{a} lent a {obj} to {b}.the person who received the {obj} was {b}.",
                   "{a} handed a {obj} to {b}.the person who received the {obj} was {b}.",
                   "{a} gave {b} a {obj}.the person who gave the {obj} was {a}."]
    call_frames = ["{a} called {b}.{b} answered the call from {a}.",
                   "{a} phoned {b}.{b} answered the call from {a}.",
                   "{a} called {b}.{b} picked up the call from {a}.",
                   "{a} called {b}.{b} answered and thanked {a}.",
                   "{a} wrote to {b}.{b} answered the letter from {a}."]
    lines = []
    for a in NAMES:  # every ordered pair of people once as a gift story, a third of them as a call too
        for b in NAMES:
            if a == b or {a, b} in TEST_PAIRS:
                continue
            lines.append(rng.choice(gift_frames).format(a=a, b=b, obj=rng.choice(objects)))
            if rng.random() < 1 / 3:
                lines.append(rng.choice(call_frames).format(a=a, b=b))
    return lines


def clean(lines):
    """Drop anything that overlaps a test item, then dedupe."""
    kept = []
    for line in dict.fromkeys(lines):
        text = normalized(line)
        if matching_cases(line, SUITE) or any(first in text for first in FIRST_SENTENCES):
            continue
        kept.append(line)
    return kept


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "corpus"
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(2026)
    for name, build in [("grammar", grammar), ("opposites", opposites), ("negation", negation), ("reference", reference)]:
        chosen = sorted(clean(build(rng)))
        assert not matching_cases("\n".join(chosen), SUITE)
        (out / f"{name}.txt").write_text("\n".join(chosen) + "\n", encoding="utf-8")
        print(f"{name}: {len(chosen)} passages -> {out / f'{name}.txt'}")


if __name__ == "__main__":
    main()
