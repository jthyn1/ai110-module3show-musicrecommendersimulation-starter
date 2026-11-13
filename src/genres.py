"""
Hand-picked genre families used to give partial credit for related genres.

Each main genre maps to a list of sub-genres (kept under ~100 per family).
A sub-genre can appear in more than one family (e.g. "pop punk" is in both
pop and rock, "lofi" is in both hip-hop and electronic).
"""

import re
from typing import Set

GENRE_FAMILIES = {
    "pop": [
        "pop", "indie pop", "k-pop", "j-pop", "c-pop", "synth-pop", "electropop",
        "dance pop", "teen pop", "art pop", "dream pop", "bubblegum pop", "power pop",
        "chamber pop", "baroque pop", "hyperpop", "bedroom pop", "sophisti-pop",
        "europop", "britpop", "city pop", "latin pop", "pop rock", "pop punk",
        "acoustic pop", "adult contemporary", "alt-pop", "folk pop", "country pop",
        "pop soul", "sunshine pop", "jangle pop", "noise pop", "twee pop",
        "psychedelic pop", "operatic pop", "traditional pop", "pop rap",
    ],
    "rock": [
        "rock", "alternative rock", "indie rock", "classic rock", "hard rock",
        "soft rock", "punk", "punk rock", "pop punk", "post-punk", "hardcore punk",
        "grunge", "post-grunge", "shoegaze", "garage rock", "psychedelic rock",
        "progressive rock", "prog rock", "art rock", "glam rock", "blues rock",
        "southern rock", "folk rock", "surf rock", "rockabilly", "krautrock",
        "math rock", "post-rock", "emo", "noise rock", "stoner rock", "space rock",
        "heartland rock", "britpop", "new wave", "arena rock", "yacht rock",
        "skate punk", "ska punk", "slowcore", "dance-punk", "gothic rock",
        "industrial rock", "pop rock", "country rock", "rap rock",
    ],
    "metal": [
        "metal", "heavy metal", "thrash metal", "death metal", "black metal",
        "doom metal", "power metal", "speed metal", "nu metal", "metalcore",
        "deathcore", "djent", "progressive metal", "symphonic metal", "folk metal",
        "gothic metal", "industrial metal", "sludge metal", "stoner metal",
        "glam metal", "groove metal", "alternative metal", "post-metal", "grindcore",
        "melodic death metal", "viking metal", "drone metal", "mathcore",
        "rap metal", "funk metal", "kawaii metal", "nwobhm",
    ],
    "jazz": [
        "jazz", "bebop", "hard bop", "cool jazz", "smooth jazz", "free jazz", "swing",
        "big band", "dixieland", "jazz fusion", "acid jazz", "latin jazz",
        "bossa nova", "modal jazz", "gypsy jazz", "vocal jazz", "soul jazz",
        "nu jazz", "post-bop", "ragtime", "avant-garde jazz", "jazz funk",
        "jazz rap", "chamber jazz", "ethio-jazz", "spiritual jazz", "lounge",
    ],
    "hip-hop": [
        "hip-hop", "rap", "trap", "drill", "uk drill", "boom bap", "gangsta rap",
        "conscious hip-hop", "alternative hip-hop", "jazz rap", "lofi", "lofi hip-hop",
        "cloud rap", "emo rap", "mumble rap", "grime", "crunk", "g-funk",
        "horrorcore", "phonk", "east coast hip-hop", "west coast hip-hop",
        "southern hip-hop", "dirty south", "trip hop", "underground hip-hop",
        "hyphy", "bounce", "chopped and screwed", "afro trap", "pop rap",
        "rap rock", "rap metal", "k-hip-hop", "latin trap", "country rap",
    ],
    "electronic": [
        "electronic", "edm", "house", "deep house", "tech house", "progressive house",
        "acid house", "techno", "minimal techno", "trance", "dubstep",
        "drum and bass", "dnb", "jungle", "uk garage", "breakbeat", "ambient",
        "dark ambient", "drone", "chillwave", "synthwave", "vaporwave", "retrowave",
        "darkwave", "electro", "electroclash", "electro swing", "idm", "glitch",
        "downtempo", "chillout", "trip hop", "future bass", "big room", "hardstyle",
        "gabber", "footwork", "moombahton", "eurodance", "dance", "industrial",
        "lofi", "new age", "synth-pop", "electropop",
    ],
    "r&b": [
        "r&b", "rnb", "rhythm and blues", "contemporary r&b", "alternative r&b",
        "soul", "neo soul", "pop soul", "northern soul", "psychedelic soul",
        "funk", "p-funk", "motown", "quiet storm", "new jack swing", "disco",
        "boogie", "gospel", "doo-wop",
    ],
    "country": [
        "country", "country pop", "country rock", "country rap", "bluegrass",
        "americana", "outlaw country", "honky tonk", "alt-country", "western",
        "western swing", "red dirt", "bro-country", "cowpunk", "nashville sound",
        "bakersfield sound", "texas country", "traditional country",
        "neotraditional country", "cajun", "zydeco",
    ],
    "folk": [
        "folk", "indie folk", "folk rock", "folk pop", "folk punk", "folk metal",
        "contemporary folk", "traditional folk", "singer-songwriter", "acoustic",
        "americana", "bluegrass", "celtic", "freak folk", "anti-folk",
        "chamber folk", "neofolk", "psych folk", "sea shanty", "appalachian folk",
    ],
    "classical": [
        "classical", "baroque", "romantic era", "classical period", "opera",
        "orchestral", "chamber music", "symphony", "minimalism",
        "contemporary classical", "neoclassical", "modern classical", "choral",
        "early music", "renaissance", "medieval", "impressionist", "film score",
        "soundtrack", "string quartet", "art song",
    ],
    "reggae": [
        "reggae", "roots reggae", "dub", "dancehall", "ska", "rocksteady",
        "lovers rock", "ragga", "reggae fusion", "dub poetry", "two tone",
    ],
    "blues": [
        "blues", "delta blues", "chicago blues", "electric blues", "blues rock",
        "country blues", "piedmont blues", "jump blues", "texas blues",
        "soul blues", "rhythm and blues", "boogie-woogie", "swamp blues",
        "hill country blues", "british blues",
    ],
    "latin": [
        "latin", "reggaeton", "salsa", "bachata", "merengue", "cumbia", "latin pop",
        "latin jazz", "latin trap", "bossa nova", "samba", "tango", "mariachi",
        "banda", "corridos", "son cubano", "bolero", "tejano", "norteno", "dembow",
    ],
}


def normalize_genre(genre: str) -> str:
    """Lowercases a genre and strips spaces, hyphens, and symbols ("K-Pop" -> "kpop")."""
    return re.sub(r"[^a-z0-9]", "", genre.lower())


def families_of(genre: str) -> Set[str]:
    """Returns the names of every main-genre family that lists this genre."""
    target = normalize_genre(genre)
    return {
        family
        for family, members in GENRE_FAMILIES.items()
        if target in {normalize_genre(m) for m in members}
    }
