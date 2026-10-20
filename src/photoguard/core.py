"""Local-only preview protection. Never modifies or exports high-quality originals."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
import hashlib
import json
import math
import os
import re
import tempfile

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp'}

@dataclass(frozen=True)
class Options:
    text: str = 'PRÉVIA • NÃO COMPRADA'
    max_size: int = 1100
    opacity: int = 130
    density: int = 4
    quality: int = 76
    grid: bool = True
    blur: float = 0.0  # Reserved for later experimental processing; intentionally unused

    def validate(self):
        if not self.text.strip() or len(self.text) > 120:
            raise ValueError('Texto deve ter de 1 a 120 caracteres.')
        if not 320 <= self.max_size <= 3000:
            raise ValueError('Resolução deve ser de 320 a 3000 pixels.')
        if not 30 <= self.opacity <= 240:
            raise ValueError('Opacidade deve ser de 30 a 240.')
        if not 2 <= self.density <= 9:
            raise ValueError('Densidade deve ser de 2 a 9.')
        if not 40 <= self.quality <= 95:
            raise ValueError('Qualidade deve ser de 40 a 95.')


def _font(size: int):
    candidates = [
        'C:/Windows/Fonts/arialbd.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def create_preview(source: Path, destination: Path, options: Options) -> dict:
    """Creates a visibly watermarked reduced-resolution JPEG at destination."""
    options.validate()
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if source == destination:
        raise ValueError('Nunca sobrescreva a imagem original.')
    if destination.is_relative_to(source.parent) and destination.name == source.name:
        raise ValueError('Origem e saída devem ser diferentes.')
    with Image.open(source) as raw:
        image = ImageOps.exif_transpose(raw).convert('RGB')
        image.thumbnail((options.max_size, options.max_size), Image.Resampling.LANCZOS)
    w, h = image.size
    # Transparent overlay tiled across the subject; rotation and alternating offsets.
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    cell_w = max(130, w // options.density)
    cell_h = max(100, h // options.density)
    font = _font(max(13, int(min(w,h) * .037)))
    stamp = Image.new('RGBA', (cell_w * 2, cell_h), (0,0,0,0))
    d = ImageDraw.Draw(stamp)
    word = options.text
    bbox = d.textbbox((0,0), word, font=font, stroke_width=1)
    text_w = bbox[2] - bbox[0]
    if text_w > cell_w * 1.65:
        font = _font(max(11, int(min(w,h) * .020)))
    d.text((cell_w, cell_h//2), word, anchor='mm', font=font,
           fill=(255,255,255,options.opacity), stroke_width=1,
           stroke_fill=(10,15,25, min(215,options.opacity+60)))
    rotated = stamp.rotate(17, resample=Image.Resampling.BICUBIC, expand=True)
    rw,rh = rotated.size
    for row, y in enumerate(range(-rh, h+rh, cell_h)):
        for x in range(-rw, w+rw, cell_w*2):
            overlay.alpha_composite(rotated, (x + (cell_w if row%2 else 0), y))
    if options.grid:
        grid = ImageDraw.Draw(overlay)
        # Slight irregular line placement to increase the cost of simple cloning.
        step = max(55, min(w,h)//(options.density*2))
        for i, y in enumerate(range(-w, h+w, step)):
            jitter = (i*13) % 17 - 8
            grid.line((0, y+jitter, w, y+w+jitter), fill=(245,245,245,38), width=max(1,w//1000))
            grid.line((0, y+jitter+w//4, w, y-w*3//4+jitter), fill=(0,0,0,28), width=1)
    image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write; never include source EXIF/GPS metadata.
    fd, temp_name = tempfile.mkstemp(prefix='.photoguard-', suffix='.jpg', dir=str(destination.parent))
    os.close(fd)
    try:
        image.save(temp_name, format='JPEG', quality=options.quality, optimize=True, progressive=True)
        os.replace(temp_name, destination)
    finally:
        if os.path.exists(temp_name): os.unlink(temp_name)
    return {'source':str(source),'preview':str(destination),'width':w,'height':h,
            'source_sha256':_sha256(source)}


def _sha256(path):
    hashobj = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): hashobj.update(chunk)
    return hashobj.hexdigest()


def process_directory(input_dir: Path, output_dir: Path, options: Options, progress=None) -> dict:
    input_dir, output_dir = Path(input_dir).resolve(), Path(output_dir).resolve()
    if not input_dir.is_dir():
        raise ValueError('Pasta de entrada não existe.')
    if input_dir == output_dir or output_dir.is_relative_to(input_dir):
        raise ValueError('Saída deve ficar fora da pasta dos originais para impedir reprocessamento.')
    photos = sorted(p for p in input_dir.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED)
    report = {'version':'0.1.0','images':[],'errors':[],'count':len(photos)}
    for index, photo in enumerate(photos, 1):
        relative = photo.relative_to(input_dir)
        # Preserve folder hierarchy; include source extension to avoid JPG/PNG filename collisions.
        target = output_dir / relative.parent / f'{relative.stem}_{relative.suffix[1:].lower()}_preview.jpg'
        try:
            report['images'].append(create_preview(photo,target,options))
            msg = f'{index}/{len(photos)} ✓ {relative}'
        except Exception as e:
            report['errors'].append({'file':str(relative),'error':str(e)})
            msg = f'{index}/{len(photos)} ERRO {relative}: {e}'
        if progress: progress(msg)
    output_dir.mkdir(parents=True,exist_ok=True)
    with (output_dir/'photoguard-report.json').open('w',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
    return report
