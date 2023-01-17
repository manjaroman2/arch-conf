import math
from pathlib import Path
import shutil
import tarfile

home = Path.home()
files = [
    home / ".config/picom/picom.conf", 
    home / ".config/alacritty/alacritty.yml",
    home / ".config/awesome/rc.lua",
    home / ".config/awesome/themes/",
    home / ".bashrc",
    home / ".nvimrc",
    home / ".xinitrc"
]

compression = "xz" # gz, bz2
backup = Path.cwd() / "backup"


if not backup.is_dir():
    if backup.exists():
        ow = input(
            f"File {backup} already exists. Do you want to delete it? [y/N] " or "N")
        if ow != "y":
            exit(1)
        backup.unlink()
    backup.mkdir()
else:
    if f := list(backup.glob("./*")):
        ow = input(
            f"{len(f)} files exist in {backup}. \nDo you want to delete everything in the directory? [y/N] " or "N")
        if ow != "y":
            exit(1)
        shutil.rmtree(backup)
        backup.mkdir()

for f in files:
    if not f.exists():
        print(f"{f} does not exist. Skipping")
        continue
    p = backup / f.relative_to(home)
    if not p.parent.exists():
        p.parent.mkdir(parents=True)
    if f.is_dir():
        shutil.copytree(f, p)
    else:
        shutil.copyfile(f, p)
    print(f"  {f} -> {p}")


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def make_tarfile(output_filename, source_dir: Path, compression="xz"):
    with tarfile.open(output_filename, f"w:{compression}") as tar:
        tar.add(source_dir, arcname=source_dir.stem)


def dirsize(path):
    import os
    return sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(path) for filename in filenames)


c = f".{compression}" if compression else ""
backup_compressed = backup.parent / f"backup.tar{c}"
print(f"Compressing {compression} file: {backup_compressed.name}")
make_tarfile(backup_compressed, backup, compression)

bs = dirsize(backup)
bcs = backup_compressed.stat().st_size
print(
    f"Backup size: {convert_size(bs)}\t>>>\t{convert_size(bcs)} compressed ({round(bcs/bs*100, 1)}%)")
shutil.rmtree(backup) 
