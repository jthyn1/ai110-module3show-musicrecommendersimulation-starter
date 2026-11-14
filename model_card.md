# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**GenreGenie 1.0**

---

## 2. Intended Use

**Goal / task:** GenreGenie suggests the 5 songs from a small catalog that best fit one listener's stated taste. It predicts "how well does this song fit what you said you like?" and explains every pick.

**Intended use:**

- Classroom exploration of how content-based recommenders turn data into rankings.
- Trying out different taste profiles and weights to see how the ranking changes.

**Assumptions about the user:** the user can describe their taste with one favorite genre, one favorite mood, a target energy and valence (0 to 1), and whether they like acoustic music. It assumes that taste stays the same and doesn't depend on the situation.

**Not intended for:**

- Real users or a real product. The catalog is 20 made-up songs.
- Judging whether a song or artist is "good". A low score only means "not close to this one profile".
- Anyone whose taste spans many genres or changes with context (workout vs. study). One profile can't represent that.
- Making decisions about artists (payouts, promotion), because the scores reflect hand-picked weights, not listener behavior.

---

## 3. How the Model Works

Every song is graded against the user's profile, like a checklist:

- **Same genre as the user's favorite:** +2 points. **A related genre** gets +1 instead. "Related" means one name is inside the other (like "k-pop" and "pop") or both are listed in the same family in a hand-made genre map (like "grunge" and "rock").
- **Same mood:** +1 point.
- **Energy:** up to +1 point, depending on how *close* the song's energy is to the user's target. Exactly on target gets the full point. Far away gets almost nothing. Being louder or calmer than the target doesn't help by itself, only being close does.
- **Valence (how happy or positive it sounds):** up to +1 point, scored the same way as energy.
- **Acoustic bonus:** +0.5 if the user likes acoustic music and the song is mostly acoustic.

The points are added up (max 5.5), the songs are sorted from highest to lowest, and the top 5 are shown. Each recommendation lists the reasons that earned its points.

**Changes from the starter:** the starter's suggested recipe was genre + mood + energy. I added valence closeness, the acoustic bonus (so the profile's `likes_acoustic` setting actually does something), and partial credit for related genres.

---

## 4. Data

- **20 songs** in `data/songs.csv`: the 10 starter songs plus 10 I added.
- **Genres:** pop, indie pop, k-pop, lofi (3 songs), rock, metal, ambient, jazz, synthwave, hip-hop, classical, country, r&b, edm, folk, reggae, blues. Most genres have only one song.
- **Moods:** happy, chill, intense, relaxed, moody, focused, confident, peaceful, angry, nostalgic, romantic, energetic, sad, uplifting, melancholy.
- **Features per song:** genre, mood, energy, tempo, valence, danceability, acousticness. Tempo and danceability are loaded but not used in scoring.
- **What I added:** 10 songs in genres and moods the starter didn't have (hip-hop, classical, metal, country, r&b, edm, folk, reggae, k-pop, blues).
- **What's missing:** lyrics, language, artist popularity, release year, and any listening history. Most genres have a single song, so the catalog can't show variety *within* a genre. Each song has exactly one genre and one mood, while real songs often blend several.

---

## 5. Strengths

- **Clear single-genre tastes work well.** For Chill Lofi, the top 4 are the three lofi tracks and the ambient track, all calm, chill and acoustic. For Deep Intense Rock, the only rock song (Storm Runner) wins by a wide margin.
- **Related genres help.** For High-Energy Pop, indie pop (Rooftop Lights) and k-pop (Starlight Dash) land at #2 and #3, ahead of the "pop but intense" Gym Hero. That matches what a happy-pop listener probably wants.
- **Closeness scoring behaves sensibly.** A song only gets energy points for being near the target. Wanting 0.35 energy doesn't hand points to every quiet song or every loud one.
- **Every pick explains itself.** The reasons make it easy to see *why* a song placed where it did, which is how I found the problems below.

---

## 6. Limitations and Bias

**Main weakness: the hand-made genre map decides who counts as "related", and it is uneven.** In my genre map, lofi belongs to both the hip-hop and electronic families, so for the Chill Lofi profile an upbeat hip-hop track (Concrete Crown, energy 0.78) gets +1 "related genre" and ranks #5, ahead of Coffee Shop Stories, a calm acoustic jazz song that fits the chill vibe much better. Meanwhile, metal and rock are separate families, so the Deep Intense Rock profile gives Iron Tide (metal, energy 0.97) no genre credit at all, and it ranks below a synthwave song. The +1 for a related genre is worth as much as a perfect energy match, so my labeling choices end up mattering more than how the music actually sounds. Users whose genres I grouped generously get more relevant-looking picks than users whose genres I left alone.

**Other limitations:**

- **Genre outweighs everything else.** An exact genre match (+2.0) is worth more than a perfect energy and valence fit combined, so a "pop but intense" gym song (Gym Hero) still beats non-pop songs that fit the happy mood better.
- **Uneven catalog.** Lofi has 3 songs and most genres have 1. A lofi fan gets a full list of lofi, but a rock fan gets one rock song and then filler from whatever is closest in energy.
- **Exact-word moods.** "sad" and "melancholy" count as completely different moods, so near-synonyms get no credit.
- **Substring matching can misfire.** Because "k-pop" contains "pop", any genre name that contains another one gets credit, even when the overlap is accidental (for example "ska" inside "skatepunk").
- **The acoustic bonus can pull against energy.** For a metal fan who also likes acoustic music, a mid-energy country song (Dirt Road Letters) ranks #2, above an EDM track whose energy matches exactly.
- **Missing preferences become ties.** An empty profile scores every song 0, and the list just falls back to alphabetical order.

---

## 7. Evaluation

### Profiles tested

My own profile, three "normal" profiles, and three edge cases meant to trick the scoring:

| Profile | Settings | What it tests |
|---|---|---|
| Me | metal, intense, energy 0.9, valence 0.4 | My own taste. It has the same targets as Deep Intense Rock, so only the genre differs |
| High-Energy Pop | pop, happy, energy 0.8, valence 0.85 | The starter's default pop/happy case, plus related-genre credit |
| Chill Lofi | lofi, chill, energy 0.35, valence 0.6, likes acoustic | Low energy plus the acoustic bonus |
| Deep Intense Rock | rock, intense, energy 0.9, valence 0.4 | A genre with only one song in the catalog |
| Edge: Genre Not In Catalog | polka, happy, energy 0.6 | What happens when genre points can never be earned |
| Edge: Acoustic Headbanger | metal, energy 0.95, likes acoustic | Conflicting preferences (acoustic songs are all low energy) |
| Edge: Empty Profile | nothing | No preferences at all |

### Results (`python -m src.main`)

```
Loaded songs: 20

=== Me (genre=metal, mood=intense, energy=0.9, valence=0.4, likes_acoustic=False) ===
 1. Iron Tide (Black Anvil)              3.75  genre match (+2.0); energy 0.97 vs 0.90 (+0.93); valence 0.22 vs 0.40 (+0.82)
 2. Storm Runner (Voltline)              2.91  mood match (+1.0); energy 0.91 vs 0.90 (+0.99); valence 0.48 vs 0.40 (+0.92)
 3. Gym Hero (Max Pulse)                 2.60  mood match (+1.0); energy 0.93 vs 0.90 (+0.97); valence 0.77 vs 0.40 (+0.63)
 4. Night Drive Loop (Neon Echo)         1.76  energy 0.75 vs 0.90 (+0.85); valence 0.49 vs 0.40 (+0.91)
 5. Concrete Crown (Verse Theory)        1.66  energy 0.78 vs 0.90 (+0.88); valence 0.62 vs 0.40 (+0.78)

=== High-Energy Pop (genre=pop, mood=happy, energy=0.8, valence=0.85, likes_acoustic=False) ===
 1. Sunrise City (Neon Echo)             4.97  genre match (+2.0); mood match (+1.0); energy 0.82 vs 0.80 (+0.98); valence 0.84 vs 0.85 (+0.99)
 2. Rooftop Lights (Indigo Parade)       3.92  related genre indie pop ~ pop (+1.0); mood match (+1.0); energy 0.76 vs 0.80 (+0.96); valence 0.81 vs 0.85 (+0.96)
 3. Starlight Dash (NOVA9)               3.87  related genre k-pop ~ pop (+1.0); mood match (+1.0); energy 0.88 vs 0.80 (+0.92); valence 0.90 vs 0.85 (+0.95)
 4. Gym Hero (Max Pulse)                 3.79  genre match (+2.0); energy 0.93 vs 0.80 (+0.87); valence 0.77 vs 0.85 (+0.92)
 5. Bassline Voltage (Kilowatt Kids)     1.80  energy 0.95 vs 0.80 (+0.85); valence 0.80 vs 0.85 (+0.95)

=== Chill Lofi (genre=lofi, mood=chill, energy=0.35, valence=0.6, likes_acoustic=True) ===
 1. Library Rain (Paper Lanterns)        5.50  genre match (+2.0); mood match (+1.0); energy 0.35 vs 0.35 (+1.00); valence 0.60 vs 0.60 (+1.00); acoustic sound (+0.5)
 2. Midnight Coding (LoRoom)             5.39  genre match (+2.0); mood match (+1.0); energy 0.42 vs 0.35 (+0.93); valence 0.56 vs 0.60 (+0.96); acoustic sound (+0.5)
 3. Focus Flow (LoRoom)                  4.44  genre match (+2.0); energy 0.40 vs 0.35 (+0.95); valence 0.59 vs 0.60 (+0.99); acoustic sound (+0.5)
 4. Spacewalk Thoughts (Orbit Bloom)     4.38  related genre ambient ~ lofi (+1.0); mood match (+1.0); energy 0.28 vs 0.35 (+0.93); valence 0.65 vs 0.60 (+0.95); acoustic sound (+0.5)
 5. Concrete Crown (Verse Theory)        2.55  related genre hip-hop ~ lofi (+1.0); energy 0.78 vs 0.35 (+0.57); valence 0.62 vs 0.60 (+0.98)

=== Deep Intense Rock (genre=rock, mood=intense, energy=0.9, valence=0.4, likes_acoustic=False) ===
 1. Storm Runner (Voltline)              4.91  genre match (+2.0); mood match (+1.0); energy 0.91 vs 0.90 (+0.99); valence 0.48 vs 0.40 (+0.92)
 2. Gym Hero (Max Pulse)                 2.60  mood match (+1.0); energy 0.93 vs 0.90 (+0.97); valence 0.77 vs 0.40 (+0.63)
 3. Night Drive Loop (Neon Echo)         1.76  energy 0.75 vs 0.90 (+0.85); valence 0.49 vs 0.40 (+0.91)
 4. Iron Tide (Black Anvil)              1.75  energy 0.97 vs 0.90 (+0.93); valence 0.22 vs 0.40 (+0.82)
 5. Concrete Crown (Verse Theory)        1.66  energy 0.78 vs 0.90 (+0.88); valence 0.62 vs 0.40 (+0.78)

=== Edge: Genre Not In Catalog (genre=polka, mood=happy, energy=0.6) ===
 1. Rooftop Lights (Indigo Parade)       1.84  mood match (+1.0); energy 0.76 vs 0.60 (+0.84)
 2. Sunrise City (Neon Echo)             1.78  mood match (+1.0); energy 0.82 vs 0.60 (+0.78)
 3. Starlight Dash (NOVA9)               1.72  mood match (+1.0); energy 0.88 vs 0.60 (+0.72)
 4. Island Time (Sol Rocker)             1.00  energy 0.60 vs 0.60 (+1.00)
 5. Dirt Road Letters (Hollis Grey)      0.95  energy 0.55 vs 0.60 (+0.95)

=== Edge: Acoustic Headbanger (genre=metal, energy=0.95, likes_acoustic=True) ===
 1. Iron Tide (Black Anvil)              2.98  genre match (+2.0); energy 0.97 vs 0.95 (+0.98)
 2. Dirt Road Letters (Hollis Grey)      1.10  energy 0.55 vs 0.95 (+0.60); acoustic sound (+0.5)
 3. Bassline Voltage (Kilowatt Kids)     1.00  energy 0.95 vs 0.95 (+1.00)
 4. Gym Hero (Max Pulse)                 0.98  energy 0.93 vs 0.95 (+0.98)
 5. Midnight Coding (LoRoom)             0.97  energy 0.42 vs 0.95 (+0.47); acoustic sound (+0.5)

=== Edge: Empty Profile (no preferences) ===
 1. Bassline Voltage (Kilowatt Kids)     0.00  no preferences matched
 2. Coffee Shop Stories (Slow Stereo)    0.00  no preferences matched
 3. Concrete Crown (Verse Theory)        0.00  no preferences matched
 4. Dirt Road Letters (Hollis Grey)      0.00  no preferences matched
 5. Empty Station Blues (Earl Mason)     0.00  no preferences matched
```

### What surprised me

- **Gym Hero shows up for both Happy Pop and Intense Rock.** For the pop listener it sits at #4: it gets the full 2 points just for being labeled "pop", even though its mood is "intense", not "happy". For the rock listener it ranks #2, without being rock at all, because it matches the "intense" mood and its energy (0.93) is almost exactly the 0.9 target. In plain words: the system doesn't hear the song. It only checks labels and numbers, and Gym Hero ticks enough boxes for both people.
- **Why Sunrise City is #1 for High-Energy Pop:** it earns every point it can. Genre is pop (+2.0), mood is happy (+1.0), energy 0.82 is 0.02 from the target (+0.98), and valence 0.84 is 0.01 away (+0.99), for 4.97 out of a possible 5.0 (this profile doesn't like acoustic, so the 0.5 bonus is off the table).
- **Upbeat hip-hop shows up for a chill lofi listener** (see Limitations): the genre-family link outweighs a big energy mismatch.
- **Metal gets no love from the rock profile**, because the genre map treats them as unrelated.

### Comparing profiles (pairwise)

| Pair | What changed and why it makes sense |
|---|---|
| Me vs Deep Intense Rock | Same mood, energy, and valence targets. Only the genre is different. Iron Tide jumps from #4 to #1 and Storm Runner drops from #1 to #2, while #3–5 stay the same. My top score is lower (3.75 vs 4.91) because Iron Tide's mood is "angry", not "intense". This is the clearest proof that the genre label alone can reorder the top of the list. |
| Me vs High-Energy Pop | Only Gym Hero is in both lists. My low valence target (0.4) pushes the bright, happy pop songs out. |
| Me vs Chill Lofi | Opposite energy targets. The only shared song is Concrete Crown at #5, for different reasons: the lofi list gets it through the hip-hop family link, and mine gets it from energy closeness. |
| Me vs Genre Not In Catalog | No songs in common. Polka wants happy, mid-energy songs, and I want intense, high-energy ones. |
| Me vs Acoustic Headbanger | Both are metal, so Iron Tide is #1 in both, and Gym Hero appears in both on energy. After that the acoustic bonus pulls country and lofi into the headbanger's list, while my "intense" mood pulls in Storm Runner instead. |
| Me vs Empty Profile | I get a clear metal winner. The empty profile gets an alphabetical list. |
| High-Energy Pop vs Chill Lofi | Completely different lists. Pop picks upbeat, happy songs around 0.8 energy, while lofi picks quiet, acoustic tracks around 0.35. Energy and the acoustic bonus pull them to opposite ends of the catalog. |
| High-Energy Pop vs Deep Intense Rock | Both want high energy, so Gym Hero appears in both. Pop gets it through genre, rock through mood and energy. Rock's lower valence target (0.4) pushes the bright pop songs out and darker songs like Night Drive Loop and Iron Tide in. |
| High-Energy Pop vs Genre Not In Catalog | Same "happy" mood, so the three happy pop-family songs top both lists, but polka earns no genre points. The scores drop from about 4–5 to under 2, and #4–5 are filled purely by energy closeness to 0.6. |
| High-Energy Pop vs Acoustic Headbanger | No overlap except edm and Gym Hero, which have energy near both targets. The metal song wins the headbanger list on genre, while the acoustic bonus drags in country and lofi songs that a pop fan never sees. |
| High-Energy Pop vs Empty Profile | Pop has a clear winner (4.97). The empty profile scores everything 0 and lists songs alphabetically, which shows the ranking only means something when the user gives preferences. |
| Chill Lofi vs Deep Intense Rock | Opposites: lofi favors low energy and acoustic songs, rock favors high energy and low valence. No song appears in both top 5s except Concrete Crown, which sneaks into lofi via the genre family and into rock via energy. |
| Chill Lofi vs Genre Not In Catalog | Lofi scores near the maximum (5.5) because it matches genre, mood and energy. Polka can only earn mood and energy points, so its top score is 1.84. Lofi fans are better served simply because the catalog has 3 lofi songs. |
| Chill Lofi vs Acoustic Headbanger | Both like acoustic music, but lofi's low energy target agrees with the acoustic bonus, while the headbanger's 0.95 energy fights it. So lofi gets a clean list and the headbanger gets a mixed one (metal, then country, then edm). |
| Chill Lofi vs Empty Profile | Lofi hits a perfect 5.50 with Library Rain. The empty profile can't tell any songs apart. |
| Deep Intense Rock vs Genre Not In Catalog | Rock has one real match and then falls back to energy filler. Polka has no real match at all and falls back to mood plus energy. Both show what happens when the catalog doesn't have enough of your genre. |
| Deep Intense Rock vs Acoustic Headbanger | Both are high energy, and both list Iron Tide, which ranks #4 for rock (no genre credit) but #1 for the metal fan (genre match). The exact same song moves from #4 to #1 purely because of the genre label. |
| Deep Intense Rock vs Empty Profile | Rock's list is driven by energy and valence after the first song. The empty list is alphabetical, with no signal at all. |
| Genre Not In Catalog vs Acoustic Headbanger | Both lose a lot of points: polka has no genre match, and the headbanger has no mood. Their lists are mostly decided by energy closeness to 0.6 vs 0.95, which is why one gets mid-tempo songs and the other gets the loudest ones. |
| Genre Not In Catalog vs Empty Profile | Polka still produces a sensible list because mood and energy carry it. The empty profile can't. Even partial preferences give the system something to work with. |
| Acoustic Headbanger vs Empty Profile | The headbanger at least gets the right #1 (Iron Tide), then a mix. The empty profile gets nothing meaningful. |

### Experiment: weight shift (genre halved, energy doubled)

I temporarily changed the weights to exact genre 1.0 (from 2.0), related genre 0.5 (from 1.0) and energy 2.0 (from 1.0), ran the program again, and then put the weights back. The maximum score stayed 5.5, so the math is still balanced. The full before/after is in the README under **Experiments You Tried**.

- **More accurate for Chill Lofi:** the upbeat hip-hop track dropped out and the calm acoustic jazz song (Coffee Shop Stories) took its place.
- **More accurate for Acoustic Headbanger:** the low-energy country and lofi songs fell out, and high-energy tracks (edm, Gym Hero, Storm Runner) filled the list.
- **More accurate for Deep Intense Rock:** the metal song Iron Tide moved up from #4 to #3, above synthwave.
- **Just different for High-Energy Pop:** the top 4 stayed the same and #5 swapped edm for hip-hop.

Overall, giving genre less weight made the lists match the *vibe* better, mostly because it shrank the effect of my uneven genre-family map.

---

## 8. Future Work

- **Lower the genre weight or make it a sliding scale.** The experiment showed that rankings feel better when energy counts more than the genre label, and a "how related" score (instead of a flat +1) would make the genre map less all-or-nothing.
- **Group similar moods** (sad/melancholy, chill/relaxed/peaceful) so near-synonyms get partial credit, the same way related genres do.
- **Add variety to the top 5**, for example at most two songs from the same genre or artist, so a lofi fan also sees something new.
- **Use more features.** Tempo and danceability are already in the data but unused, and a profile could have more than one favorite genre.

---

## 9. Personal Reflection

**Biggest learning moment.** I was honestly expecting a lot more identifiers to be considered when categorizing music, things like pitch, vocal timbre, and instrumentation. For a simple implementation like this, the ones we chose (genre, mood, energy, valence, acousticness) make sense, but it showed me how much a real system has to leave out or learn some other way.

**Genre matching decision.** I chose to give partial credit to related genres, including names that aren't separate words, because k-pop is a subgenre of pop and should count as one. Lofi also counts as part of hip-hop (though a bit far removed). I deliberately left metal and rock as separate families: despite having similar origins, they still feel like very different genres today. Seeing the results, I'd keep that setup.

**How AI helped, and when I double-checked it.** Using AI helped automate the actual creation of the project while streamlining decision making, but verification and the final decisions were still left up to me. The result is a project that still feels like my own, but that could be rapidly prototyped and delivered, so the functionality and design became the real workflow rather than the production. Because my workflow had the AI stop and ask me about each design decision, there was little that needed to be double-checked afterward. A good example of where I stepped in was how k-pop and other genres that aren't separate words should be classified: the AI's first suggestion only matched whole words, and I changed it so k-pop counts as pop.

**How the results felt.** The recommendations did feel correct for my own metal profile, with Iron Tide first, then Storm Runner and Gym Hero. Some things, like Concrete Crown showing up in both the lofi list and my own list, are a bit outside what I'd expect, but they score low enough not to raise concern. I added valence on top of genre, mood, and energy to try to bring the system closer to the depth of real musical taste, and in that regard it pulled its weight.

**What surprised me.** Even though the lists were mostly accurate, I still think something as complex as music is hard to pin down with just numbers, let alone genre. The lists felt fine, but there's a drawback to an algorithm recommending music instead of real people. There is untold depth in a conversation about a music recommendation, and even just knowing the personality of the person behind the recommendation helps immensely compared to an algorithm.

**What I'd try next.** I'd add a charts option that draws recommendations from what's charting in each genre (or even what isn't), or a bot that reads reviews from different music forums and recommends what's getting positively reviewed. I'd also add the extra classifiers I mentioned above, like pitch, vocal timbre, and instrumentation, as an expansion of the existing idea.
