import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

from src.genres import normalize_genre, families_of

# Algorithm recipe weights (see README "How The System Works")
GENRE_WEIGHT = 2.0          # exact genre match
RELATED_GENRE_WEIGHT = 1.0  # related genre (one name contains the other, or same family)
MOOD_WEIGHT = 1.0           # exact mood match
ENERGY_WEIGHT = 1.0         # multiplied by energy closeness (0.0-1.0)
VALENCE_WEIGHT = 1.0        # multiplied by valence closeness (0.0-1.0)
ACOUSTIC_BONUS = 0.5        # user likes acoustic and song is acoustic enough
ACOUSTIC_THRESHOLD = 0.6    # acousticness needed to count as "acoustic"

NUMERIC_INT_FIELDS = ["id"]
NUMERIC_FLOAT_FIELDS = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: Optional[float] = None


def profile_to_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile into the preference dictionary score_song expects."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "valence": user.target_valence,
        "likes_acoustic": user.likes_acoustic,
    }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k Song objects for this user, best first."""
        prefs = profile_to_prefs(user)
        scored = [(song, score_song(prefs, asdict(song))[0]) for song in self.songs]
        ranked = sorted(scored, key=lambda pair: (-pair[1], pair[0].title))
        return [song for song, _ in ranked[:max(k, 0)]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a readable explanation of why this song got its score."""
        score, reasons = score_song(profile_to_prefs(user), asdict(song))
        return explain(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Reads the songs CSV into a list of dicts with numeric fields converted to int/float."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("id"):
                continue  # skip blank lines
            for field in NUMERIC_INT_FIELDS:
                row[field] = int(row[field])
            for field in NUMERIC_FLOAT_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs


def closeness(value: float, target: float) -> float:
    """Returns 1.0 when value equals target, dropping toward 0.0 as they move apart."""
    return max(0.0, 1.0 - abs(value - target))


def genres_related(user_genre: str, song_genre: str) -> bool:
    """True if one genre name contains the other (e.g. "k-pop" / "pop") or both share a family."""
    a, b = normalize_genre(user_genre), normalize_genre(song_genre)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    return bool(families_of(user_genre) & families_of(song_genre))


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against the user's preferences and returns (score, reasons)."""
    score = 0.0
    reasons = []

    user_genre = user_prefs.get("genre") or ""
    if user_genre and normalize_genre(user_genre) == normalize_genre(song["genre"]):
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT:.1f})")
    elif genres_related(user_genre, song["genre"]):
        score += RELATED_GENRE_WEIGHT
        reasons.append(f"related genre {song['genre']} ~ {user_genre} (+{RELATED_GENRE_WEIGHT:.1f})")

    user_mood = user_prefs.get("mood") or ""
    if user_mood and user_mood.strip().lower() == song["mood"].strip().lower():
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT:.1f})")

    if user_prefs.get("energy") is not None:
        points = ENERGY_WEIGHT * closeness(song["energy"], user_prefs["energy"])
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs {user_prefs['energy']:.2f} (+{points:.2f})")

    if user_prefs.get("valence") is not None:
        points = VALENCE_WEIGHT * closeness(song["valence"], user_prefs["valence"])
        score += points
        reasons.append(f"valence {song['valence']:.2f} vs {user_prefs['valence']:.2f} (+{points:.2f})")

    if user_prefs.get("likes_acoustic") and song["acousticness"] >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_BONUS
        reasons.append(f"acoustic sound (+{ACOUSTIC_BONUS:.1f})")

    return score, reasons


def explain(reasons: List[str]) -> str:
    """Joins a song's reasons into one line, or says nothing matched."""
    return "; ".join(reasons) if reasons else "no preferences matched"


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song and returns the top k as (song, score, explanation), best first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, explain(reasons)))
    ranked = sorted(scored, key=lambda item: (-item[1], item[0]["title"]))
    return ranked[:max(k, 0)]
