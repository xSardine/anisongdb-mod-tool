# Standard libraries
from pathlib import Path
import json
import os

# External libraries
from dotenv import dotenv_values

# models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.anime.anime import Anime
from src.models.anime.anime_type import AnimeType
from src.models.anime.anime_name_type import AnimeNameType
from src.models.anime.link_anime_names import LinkAnimeName

from src.models.anime.tag import Tag
from src.models.anime.link_anime_tags import LinkAnimeTag

from src.models.anime.genre import Genre
from src.models.anime.link_anime_genres import LinkAnimeGenre

from src.models.artists.artist import Artist
from src.models.artists.artist_type import ArtistType
from src.models.artists.link_artist_names import LinkArtistName
from src.models.artists.line_up import LineUp
from src.models.artists.link_artist_line_up import LinkArtistLineUp

from src.models.songs.song import Song
from src.models.songs.song_type import SongType
from src.models.songs.link_song_artist import LinkSongArtist

# raw data
raw_data_path = Path("database/raw/")

ANIME_TYPE_MAPPING = {"TV": 1, "movie": 2, "OVA": 3, "ONA": 4, "special": 5, None: None}
ANIME_NAME_TYPE_MAPPING = {
    "Expand": 1,
    "Japanese": 2,
    "English": 3,
    "Alternative": 4,
}
SONG_CATEGORY_MAPPING = {
    "Standard": 1,
    "Chanting": 2,
    "Character": 3,
    "Instrumental": 4,
    None: None,
}
ROLE_TYPE_MAPPING = {
    "Vocalist": 1,
    "Backing vocals": 2,
    "Performer": 3,
    "Composer": 4,
    "Arranger": 5,
}


artist_id_mapping = {}


with open(raw_data_path / "song_database.json", "r", encoding="utf-8") as f:
    song_database = json.load(f)

with open(raw_data_path / "artist_database.json", "r", encoding="utf-8") as f:
    artist_database = json.load(f)

config = {
    **dotenv_values(".env.shared"),  # load shared development variables
    **dotenv_values(".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
}

sql_alchemy_uri = f'postgresql://{config["POSTGRES_USER"]}:{config["POSTGRES_PASSWORD"]}@{config["POSTGRES_HOST"]}:{config["POSTGRES_PORT"]}/{config["POSTGRES_DB"]}'


def find_artist_from_old_id(artist_id, session):
    artist = session.query(Artist).filter(
        Artist.id == artist_id_mapping[artist_id]["new_artist_id"]
    )

    if artist.count() == 0:
        return None

    if artist.count() > 1:
        print(f"Multiple artist found for id {artist_id_mapping[artist_id]}")
        return None

    return artist.first()


# Créez une connexion à la base de données
engine = create_engine(sql_alchemy_uri)
# Open a session
Session = sessionmaker(bind=engine)
session = Session()


# first pass : add artist and names
for artist_id in artist_database:
    artist = artist_database[artist_id]
    new_artist = Artist(
        **{
            "id_artist_type": 1 if not artist["members"] else 2,
        }
    )
    session.add(new_artist)
    session.flush()
    artist_id_mapping[artist_id] = {
        "old_artist_id": artist_id,
        "new_artist_id": new_artist.id,
    }

    for i, name in enumerate(artist["names"]):
        new_artist_name = LinkArtistName(
            **{
                "id_artist": new_artist.id,
                "artist_name": name,
                "order": i + 1,
            }
        )
        session.add(new_artist_name)
        session.flush()


# second pass : adding line ups
for group_id in artist_database:
    group = artist_database[group_id]

    if not group["members"]:
        continue

    update_group = find_artist_from_old_id(group_id, session)

    artist_id_mapping[group_id]["line_ups"] = {}
    for line_up_id, _ in enumerate(group["members"]):
        new_line_up = LineUp(**{"id_artist": update_group.id})
        session.add(new_line_up)
        session.flush()
        artist_id_mapping[group_id]["line_ups"][line_up_id] = {
            "old_line_up_id": line_up_id,
            "new_line_up_id": new_line_up.id,
        }

# third pass adding members in line ups
for group_id in artist_database:
    group = artist_database[group_id]

    if not group["members"]:
        continue

    for line_up_id, members in enumerate(group["members"]):
        new_line_up_id = artist_id_mapping[group_id]["line_ups"][line_up_id][
            "new_line_up_id"
        ]
        for member_id, member_line_up_id in members:
            if member_line_up_id != -1:
                new_member_line_up_id = artist_id_mapping[member_id]["line_ups"][
                    member_line_up_id
                ]["new_line_up_id"]
            else:
                new_member_line_up_id = None
            member = find_artist_from_old_id(member_id, session)
            new_link_artist_line_up = LinkArtistLineUp(
                **{
                    "id_member": member.id,
                    "id_member_line_up": new_member_line_up_id,
                    "id_role_type": ROLE_TYPE_MAPPING["Vocalist"],
                    "id_group": artist_id_mapping[group_id]["new_artist_id"],
                    "id_group_line_up": new_line_up_id,
                }
            )
            session.add(new_link_artist_line_up)
            session.flush()

for anime in song_database:
    new_anime = Anime(
        **{
            "ann_id": anime["annId"],
            "id_anime_type": ANIME_TYPE_MAPPING[anime.get("animeType", None)],
            "anime_vintage": anime.get("animeVintage", None),
        }
    )
    session.add(new_anime)
    # Flush the session to get the id assigned by the database
    session.flush()

    new_anime_name = LinkAnimeName(
        **{
            "id_anime": new_anime.id,
            "id_anime_name_type": ANIME_NAME_TYPE_MAPPING["Expand"],
            "anime_name": anime["animeExpandName"],
        }
    )
    session.add(new_anime_name)

    if anime.get("animeJPName", None):
        new_anime_name = LinkAnimeName(
            **{
                "id_anime": new_anime.id,
                "id_anime_name_type": ANIME_NAME_TYPE_MAPPING["Japanese"],
                "anime_name": anime["animeJPName"],
            }
        )
        session.add(new_anime_name)

    if anime.get("animeENName", None):
        new_anime_name = LinkAnimeName(
            **{
                "id_anime": new_anime.id,
                "id_anime_name_type": ANIME_NAME_TYPE_MAPPING["English"],
                "anime_name": anime["animeENName"],
            }
        )
        session.add(new_anime_name)

    for alt_name in anime.get("altNames", []):
        new_anime_name = LinkAnimeName(
            **{
                "id_anime": new_anime.id,
                "id_anime_name_type": ANIME_NAME_TYPE_MAPPING["Alternative"],
                "anime_name": alt_name,
            }
        )
        session.add(new_anime_name)

    session.flush()

    for tag in anime.get("tags", []):
        # check tag is not already in database
        tag_query = session.query(Tag).filter(Tag.tag == tag)
        if tag_query.count() == 0:
            new_tag = Tag(**{"tag": tag})
            session.add(new_tag)
            session.flush()
        else:
            new_tag = tag_query.first()

        # link anime to tag
        new_link_anime_tag = LinkAnimeTag(
            **{"id_anime": new_anime.id, "id_tag": new_tag.id}
        )
        session.add(new_link_anime_tag)
        session.flush()

    for genre in anime.get("genres", []):
        # check genre is not already in database
        genre_query = session.query(Genre).filter(Genre.genre == genre)

        if genre_query.count() == 0:
            new_genre = Genre(**{"genre": genre})
            session.add(new_genre)
            session.flush()
        else:
            new_genre = genre_query.first()

        # link anime to genre
        new_link_anime_genre = LinkAnimeGenre(
            **{"id_anime": new_anime.id, "id_genre": new_genre.id}
        )
        session.add(new_link_anime_genre)
        session.flush()

    for song in anime["songs"]:
        new_song = Song(
            **{
                "id_anime": new_anime.id,
                "id_song_type": song["songType"],
                "song_number": song["songNumber"] or None,
                "song_name": song["songName"],
                "song_artist": song["songArtist"],
                "id_song_category": SONG_CATEGORY_MAPPING[
                    song.get("songCategory", None)
                ],
                "song_difficulty": song.get("songDifficulty", None),
                "HQ": song["links"].get("HQ", None),
                "MQ": song["links"].get("MQ", None),
                "audio": song["links"].get("audio", None),
            }
        )

        session.add(new_song)
        session.flush()

        for artist_id, line_up_id in song["artist_ids"]:
            if line_up_id != -1:
                new_line_up_id = artist_id_mapping[artist_id]["line_ups"][line_up_id][
                    "new_line_up_id"
                ]
            else:
                new_line_up_id = None
            artist = find_artist_from_old_id(artist_id, session)
            new_link_song_artist = LinkSongArtist(
                **{
                    "id_song": new_song.id,
                    "id_artist": artist.id,
                    "id_artist_line_up": new_line_up_id,
                    "id_role_type": ROLE_TYPE_MAPPING["Vocalist"],
                }
            )
            session.add(new_link_song_artist)

        for composer_id, _ in song["composer_ids"]:
            composer = find_artist_from_old_id(composer_id, session)
            new_link_song_artist = LinkSongArtist(
                **{
                    "id_song": new_song.id,
                    "id_artist": composer.id,
                    "id_artist_line_up": None,
                    "id_role_type": ROLE_TYPE_MAPPING["Composer"],
                }
            )
            session.add(new_link_song_artist)

        for arranger_id, _ in song["arranger_ids"]:
            arranger = find_artist_from_old_id(arranger_id, session)
            new_link_song_artist = LinkSongArtist(
                **{
                    "id_song": new_song.id,
                    "id_artist": arranger.id,
                    "id_artist_line_up": None,
                    "id_role_type": ROLE_TYPE_MAPPING["Arranger"],
                }
            )
            session.add(new_link_song_artist)

        session.flush()


# save new mapping
with open(raw_data_path / "artist_id_mapping.json", "w", encoding="utf-8") as f:
    json.dump(artist_id_mapping, f, indent=4)

# close session
session.commit()
session.close()
