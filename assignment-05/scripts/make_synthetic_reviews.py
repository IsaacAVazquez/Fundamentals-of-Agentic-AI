#!/usr/bin/env python3
"""Write a synthetic reviews CSV with the same six columns as spotify_reviews_18months.csv.

The real dataset is not committed (see README). This generator exists so the pipeline,
its tests, and the fake backend can be exercised without it. The texts are templated,
not real reviews, and every output of a run over this file is marked synthetic.
"""
import argparse
import csv
import random
from datetime import datetime, timedelta

TEMPLATES = {
    "access": [
        "Can't log in since the update, keeps saying wrong password even after reset",
        "Account got locked and the login page just spins forever",
        "Logged out every day and the two factor code never arrives",
    ],
    "usability": [
        "The new layout hides the shuffle button and the ads are every two songs now",
        "Navigation is confusing, took me five minutes to find my library",
        "Too many ads, and the interface keeps changing for no reason",
    ],
    "playback": [
        "Songs stop halfway through and the app crashes when I switch tracks",
        "Playback lags constantly on wifi, skips every few seconds",
        "App freezes whenever I open a playlist and music stutters",
    ],
    "downloads": [
        "Downloaded songs disappear when I go offline, pointless for flights",
        "Offline mode says downloads are unavailable even though storage is fine",
        "Saved music won't play without internet anymore",
    ],
    "catalog": [
        "Half the songs I search for are greyed out and lyrics are missing",
        "Recommendations are all wrong and the search never finds the album",
        "Podcast I follow vanished from the catalog this week",
    ],
    "billing": [
        "Charged twice this month for premium and still shows the free plan",
        "Price went up without warning and I can't cancel from the app",
        "Paid for premium but keep hitting the paywall on every feature",
    ],
    "support": [
        "Support never answered my ticket, three weeks and nothing",
        "Chat support closed on me mid conversation and no email follow up",
        "Customer service gave a canned reply and ignored the actual issue",
    ],
    "other": [
        "Great app love it",
        "Best music app ever, five stars",
        "Meh",
        "Please add a sleep timer to the widget",
    ],
}
CANCEL_SUFFIX = [" Cancelling my subscription.", " I'm switching to another service.", " Done with this app, unsubscribing."]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--empty", type=int, default=2, help="how many rows get an empty review_text")
    parser.add_argument("--duplicates", type=int, default=50, help="how many rows reuse an earlier text exactly")
    args = parser.parse_args()
    rng = random.Random(args.seed)
    start = datetime(2022, 5, 1)
    topics = list(TEMPLATES)
    texts = []
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["review_id", "review_text", "review_rating", "review_likes", "app_version", "review_timestamp"])
        for i in range(args.rows):
            review_id = f"syn-{i:07d}"
            topic = rng.choice(topics)
            if i < args.empty:
                text = ""
            elif args.duplicates and i > 10 and rng.random() < args.duplicates / args.rows:
                text = rng.choice(texts)
            else:
                text = rng.choice(TEMPLATES[topic])
                if topic not in ("other",) and rng.random() < 0.2:
                    text += rng.choice(CANCEL_SUFFIX)
                if rng.random() < 0.05:
                    text += "\nSecond line of the same review."
            if text:
                texts.append(text)
            rating = rng.choice([1, 1, 2, 3, 4, 5]) if topic != "other" else rng.choice([4, 5, 5, 3])
            likes = rng.choice([0, 0, 0, 1, 2, 5, 12])
            version = "" if rng.random() < 0.24 else f"8.{rng.randint(7, 8)}.{rng.randint(0, 99)}.{rng.randint(100, 999)}"
            ts = start + timedelta(minutes=rng.randint(0, 18 * 30 * 24 * 60))
            writer.writerow([review_id, text, rating, likes, version, ts.strftime("%Y-%m-%d %H:%M:%S")])


if __name__ == "__main__":
    main()
