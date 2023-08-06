"""Manage media in the understory."""

import subprocess
from pathlib import Path

import web

app = web.application(
    __name__,
    prefix="media",
    args={"filename": rf"{web.nb60_re}{{4}}.\w{{1,10}}"},
    model={"media": {"mid": "TEXT", "sha256": "TEXT UNIQUE", "size": "INTEGER"}},
)

media_dir = Path("media")
media_dir.mkdir(exist_ok=True, parents=True)


@app.query
def get_media(db):
    """Return a list of media filepaths."""
    try:
        filepaths = list(media_dir.iterdir())
    except FileNotFoundError:
        filepaths = []
    return filepaths


@app.query
def create_file(db):
    """Create a media file."""
    while True:
        media_id = web.nbrandom(4)
        try:
            db.insert(
                "media",
                mid=media_id,
            )
        except db.IntegrityError:
            pass
        else:
            break
    filename = web.form("file").file.save(media_dir / media_id)
    print(str(filename))
    if str(filename).endswith(".heic"):
        subprocess.Popen(
            [
                "convert",
                filename,
                "-set",
                "filename:base",
                "%[basename]",
                f"{media_dir}/%[filename:base].jpg",
            ]
        )
    sha256 = subprocess.getoutput(f"sha256sum {filename}").split()[0]
    web.tx.db.update(
        "media",
        sha256=sha256,
        size=filename.stat().st_size,
        where="mid = ?",
        vals=[media_id],
    )
    return media_id


@app.query
def get_filepath(db, filename):
    """Return a media file's path."""
    return media_dir / filename


@app.query
def delete_file(db, filename):
    """Delete given file."""
    filepath = app.model.get_filepath(filename)
    db.delete("media", where="mid = ?", vals=[filepath.stem])
    filepath.unlink()


@app.control("")
class MediaEndpoint:
    """Your media files."""

    # owner_only = ["post"]

    def get(self):
        """Render a list of your media files."""
        media = app.model.get_media()
        try:
            query = web.form("q").q
        except web.BadRequest:
            pass
        else:
            if query == "source":
                # {
                #   "url": "https://media.aaronpk.com/2020/07/file-20200726XXX.jpg",
                #   "published": "2020-07-26T09:51:11-07:00",
                #   "mime_type": "image/jpeg"
                # }
                return {
                    "items": [
                        {
                            "url": f"{web.tx.origin}/media/{filepath.name}",
                            "published": "TODO",
                            "mime_type": "TODO",
                        }
                        for filepath in media
                    ]
                }
        return app.view.index(media)

    def post(self):
        """Create a media file."""
        media_id = app.model.create_file()
        raise web.Created(app.view.media_added(media_id), f"/{media_id}")


@app.control("{filename}")
class MediaFile:
    """A media file."""

    owner_only = ["delete"]

    def get(self, filename):
        """Return media with given filename."""
        return media_dir / filename

    def delete(self, filename):
        """Delete media with given filename."""
        app.model.delete_file(filename)
        return app.view.media_deleted()
