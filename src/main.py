"""
Command line runner for the Music Recommender Simulation.

Loads the song catalog, runs the recommender for several taste profiles,
and prints the top 5 songs for each with their score and reasons.
"""

from src.recommender import load_songs, recommend_songs

PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8, "valence": 0.85, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "valence": 0.6, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "valence": 0.4, "likes_acoustic": False},
    # Edge-case profiles meant to "trick" the scoring logic
    "Edge: Genre Not In Catalog": {"genre": "polka", "mood": "happy", "energy": 0.6},
    "Edge: Acoustic Headbanger": {"genre": "metal", "energy": 0.95, "likes_acoustic": True},
    "Edge: Empty Profile": {},
}


def describe(prefs: dict) -> str:
    """Formats a profile dictionary as 'genre=pop, mood=happy, ...'."""
    return ", ".join(f"{key}={value}" for key, value in prefs.items()) or "no preferences"


def print_recommendations(name: str, prefs: dict, songs: list, k: int = 5) -> None:
    """Prints one profile's top k recommendations, one line per song."""
    print(f"\n=== {name} ({describe(prefs)}) ===")
    for rank, (song, score, explanation) in enumerate(recommend_songs(prefs, songs, k), start=1):
        label = f"{song['title']} ({song['artist']})"
        print(f"{rank:>2}. {label:<36} {score:4.2f}  {explanation}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs)


if __name__ == "__main__":
    main()
