#!/usr/bin/env python3
"""Index local gallery files for a static GitHub Pages site."""
import argparse
import json
from pathlib import Path

ALBUMS = ('combate-medieval', 'entrenamiento', 'musica', 'congresos', 'viajes')
IMAGES = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'}
VIDEOS = {'.mp4', '.webm'}

def build(root: Path):
    result = {}
    for album in ALBUMS:
        folder = root / 'images' / album
        files = [p for p in folder.iterdir() if p.is_file() and not p.is_symlink()
                 and not p.name.startswith('.') and p.suffix.lower() in IMAGES | VIDEOS] if folder.is_dir() else []
        files.sort(key=lambda p: (not (p.stem.casefold() == 'portada' and p.suffix.lower() in IMAGES), p.name.casefold(), p.name))
        result[album] = [{'src': p.relative_to(root).as_posix(), 'type': 'image' if p.suffix.lower() in IMAGES else 'video'} for p in files]
    (root / 'media-index.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print('Indexed:', {k: len(v) for k, v in build(args.root.resolve()).items()})
