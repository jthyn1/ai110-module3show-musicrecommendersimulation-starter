from src.recommender import Song, UserProfile, Recommender, load_songs, score_song, recommend_songs, genres_related

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---- Functional API tests ----

def make_song(**overrides) -> dict:
    song = {
        "id": 1, "title": "Song", "artist": "Artist", "genre": "pop", "mood": "happy",
        "energy": 0.5, "tempo_bpm": 100.0, "valence": 0.5, "danceability": 0.5,
        "acousticness": 0.2,
    }
    song.update(overrides)
    return song


def test_load_songs_converts_numbers():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 20
    first = songs[0]
    assert isinstance(first["id"], int)
    for field in ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]:
        assert isinstance(first[field], float)


def test_exact_genre_and_mood_match_with_reasons():
    score, reasons = score_song({"genre": "pop", "mood": "happy"}, make_song())
    assert score == 3.0
    assert "genre match (+2.0)" in reasons
    assert "mood match (+1.0)" in reasons


def test_matching_ignores_case_and_hyphens():
    score, _ = score_song({"genre": "Hip Hop", "mood": "Happy"}, make_song(genre="hip-hop"))
    assert score == 3.0


def test_related_genre_by_name_gets_partial_credit():
    score, reasons = score_song({"genre": "pop"}, make_song(genre="k-pop"))
    assert score == 1.0
    assert reasons[0].startswith("related genre")


def test_related_genre_by_family_gets_partial_credit():
    assert genres_related("rock", "grunge")
    assert genres_related("grunge", "shoegaze")
    assert not genres_related("metal", "jazz")


def test_empty_genre_gets_no_genre_points():
    score, reasons = score_song({"genre": ""}, make_song())
    assert score == 0.0
    assert reasons == []


def test_energy_closeness_rewards_nearby_not_higher():
    prefs = {"energy": 0.5}
    near, _ = score_song(prefs, make_song(energy=0.55))
    far_high, _ = score_song(prefs, make_song(energy=1.0))
    assert near > far_high
    assert abs(near - 0.95) < 1e-9


def test_valence_skipped_when_not_in_profile():
    _, reasons = score_song({"energy": 0.5}, make_song())
    assert not any("valence" in r for r in reasons)


def test_acoustic_bonus_only_when_user_likes_acoustic():
    acoustic_song = make_song(acousticness=0.9)
    with_bonus, _ = score_song({"likes_acoustic": True}, acoustic_song)
    without, _ = score_song({"likes_acoustic": False}, acoustic_song)
    assert with_bonus == 0.5
    assert without == 0.0


def test_recommend_songs_sorted_and_limited_to_k():
    songs = load_songs("data/songs.csv")
    results = recommend_songs({"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=5)
    assert len(results) == 5
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)
    assert results[0][0]["title"] == "Sunrise City"
    assert isinstance(results[0][2], str) and results[0][2]


def test_recommend_songs_handles_zero_and_negative_k():
    songs = load_songs("data/songs.csv")
    assert recommend_songs({"genre": "pop"}, songs, k=0) == []
    assert recommend_songs({"genre": "pop"}, songs, k=-1) == []


def test_ties_are_broken_by_title():
    songs = [make_song(id=1, title="Beta"), make_song(id=2, title="Alpha")]
    results = recommend_songs({"genre": "pop"}, songs, k=2)
    assert [song["title"] for song, _, _ in results] == ["Alpha", "Beta"]
