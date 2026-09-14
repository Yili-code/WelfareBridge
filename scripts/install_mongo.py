"""Download only runtime files from the official Windows ZIP (omit large PDBs)."""
import io
from pathlib import Path
import shutil
import zipfile
import httpx

URL = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.2.6.zip"
ROOT = Path(__file__).resolve().parents[1]


class RemoteZip(io.RawIOBase):
    def __init__(self, client):
        self.client = client
        response = client.head(URL)
        response.raise_for_status()
        self.size = int(response.headers["content-length"])
        self.pos = 0
        self.start = 0
        self.buffer = b""

    def seekable(self):
        return True

    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def tell(self):
        return self.pos

    def read(self, size=-1):
        size = min(self.size - self.pos, size if size >= 0 else self.size)
        if size <= 0:
            return b""
        if not (self.start <= self.pos and self.pos + size <= self.start + len(self.buffer)):
            self.start = self.pos
            end = min(self.size - 1, self.pos + max(size, 4 * 1024 * 1024) - 1)
            with self.client.stream("GET", URL, headers={"Range": f"bytes={self.pos}-{end}"}) as response:
                if response.status_code != 206 or not response.headers.get("content-range", "").startswith(f"bytes {self.pos}-"):
                    raise RuntimeError("Official download server did not honor byte ranges; retry or download the ZIP manually.")
                self.buffer = response.read()
            if len(self.buffer) != end - self.start + 1:
                raise RuntimeError("Incomplete MongoDB download")
        result = self.buffer[self.pos - self.start:self.pos - self.start + size]
        self.pos += len(result)
        return result


if __name__ == "__main__":
    destination = ROOT / "data/tools/mongodb/portable/bin"
    destination.mkdir(parents=True, exist_ok=True)
    with httpx.Client(follow_redirects=True, timeout=120) as client, zipfile.ZipFile(RemoteZip(client)) as archive:
        members = [item for item in archive.infolist() if item.filename.endswith("/bin/mongod.exe") or ("/bin/" in item.filename and item.filename.endswith(".dll"))]
        if not any(item.filename.endswith("/bin/mongod.exe") for item in members):
            raise RuntimeError("mongod.exe missing from official archive")
        for item in members:
            target = destination / Path(item.filename).name
            partial = target.with_suffix(target.suffix + ".partial")
            print(f"Downloading {target.name} ({item.compress_size // 1024 // 1024} MB compressed)", flush=True)
            with archive.open(item) as source, partial.open("wb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            partial.replace(target)
    print(f"MongoDB ready: {destination / 'mongod.exe'}")
