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
    logo_path: str = ''  # Optional transparent PNG, repeated as overlay
    logo_scale: int = 32  # Percentage of preview width per watermark tile
    protection: str = 'adaptive'  # classic | adaptive | strong
    blur: float = 0.0  # Reserved for later experimental processing; intentionally unused

    def validate(self):
        if self.protection not in ('classic', 'adaptive', 'strong'):
            raise ValueError('Proteção inválida: classic, adaptive ou strong.')
        if not self.text.strip() or len(self.text) > 120:
            raise ValueError('Texto deve ter de 1 a 120 caracteres.')
        if not 320 <= self.max_size <= 3000:
            raise ValueError('Resolução deve ser de 320 a 3000 pixels.')
        if not 30 <= self.opacity <= 240:
            raise ValueError('Opacidade deve ser de 30 a 240.')
        if not 2 <= self.density <= 9:
            raise ValueError('Densidade deve ser de 2 a 9.')
        if not 10 <= self.logo_scale <= 65:
            raise ValueError('Escala da marca PNG deve ser de 10 a 65%.')
        if self.logo_path and (not Path(self.logo_path).is_file() or Path(self.logo_path).suffix.lower() != '.png'):
            raise ValueError('A marca personalizada precisa ser um arquivo PNG existente.')
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
    if options.logo_path:
        # Repeat the photographer's transparent PNG across the preview.
        with Image.open(options.logo_path) as logo_file:
            logo = logo_file.convert('RGBA')
        if not logo.width or not logo.height:
            raise ValueError('Marca PNG vazia.')
        tile_width = max(30, int(w * options.logo_scale / 100))
        tile_height = max(1, round(logo.height * tile_width / logo.width))
        logo = logo.resize((tile_width, tile_height), Image.Resampling.LANCZOS)
        alpha = logo.getchannel('A').point(lambda a: a * options.opacity // 255)
        logo.putalpha(alpha)
        pitch_x = max(1, int(tile_width * 1.4))
        pitch_y = max(1, int(tile_height * 1.8))
        for row, y in enumerate(range(-tile_height, h + tile_height, pitch_y)):
            for x in range(-tile_width, w + tile_width, pitch_x):
                overlay.alpha_composite(logo, (x + (pitch_x // 2 if row % 2 else 0), y))
    if options.grid:
        grid = ImageDraw.Draw(overlay)
        # Slight irregular line placement to increase the cost of simple cloning.
        step = max(55, min(w,h)//(options.density*2))
        for i, y in enumerate(range(-w, h+w, step)):
            jitter = (i*13) % 17 - 8
            grid.line((0, y+jitter, w, y+w+jitter), fill=(245,245,245,38), width=max(1,w//1000))
            grid.line((0, y+jitter+w//4, w, y-w*3//4+jitter), fill=(0,0,0,28), width=1)
    # Additional overlay distributed across tonal regions: not an adversarial guarantee.
    # Design is deterministic and can be recomputed for reproducible evaluations.
    if options.protection != 'classic':
        accents = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        drawer = ImageDraw.Draw(accents)
        gap = max(46, min(w, h) // (options.density * (3 if options.protection == 'strong' else 2)))
        thickness = 2 if options.protection == 'strong' else 1
        for row, cy in enumerate(range(gap // 2, h, gap)):
            for col, cx in enumerate(range(gap // 2, w, gap)):
                # alternating high and low luminance contrast avoids all-white watermarks
                sample = image.getpixel((min(w-1, cx), min(h-1, cy)))
                luminance = (299 * sample[0] + 587 * sample[1] + 114 * sample[2]) // 1000
                color = (14, 18, 29, min(200, options.opacity + 20)) if luminance > 125 else (255, 255, 255, min(205, options.opacity + 25))
                offset = ((row * 19 + col * 31) % 17) - 8
                radius = max(5, gap // (5 if options.protection == 'strong' else 7))
                x, y = cx + offset, cy
                drawer.line((x-radius, y, x+radius, y), fill=color, width=thickness)
                drawer.line((x, y-radius, x, y+radius), fill=color, width=thickness)
                if options.protection == 'strong':
                    drawer.ellipse((x-2, y-2, x+2, y+2), fill=color)
        overlay = Image.alpha_composite(overlay, accents)
    image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write; never include source EXIF/GPS metadata.
    fd, temp_name = tempfile.mkstemp(prefix='.markveil-', suffix='.jpg', dir=str(destination.parent))
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
    report = {'version':'0.5.0','images':[],'errors':[],'count':len(photos)}
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
    with (output_dir/'markveil-report.json').open('w',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
    return report
