"""Offline gallery-transformation laboratory. NOT a generative watermark removal test."""
from __future__ import annotations
import hashlib
import html
import io
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageOps, ImageStat
from .core import Options, create_preview


def _jpg(image: Image.Image, quality: int) -> Image.Image:
    buf = io.BytesIO()
    image.convert('RGB').save(buf, 'JPEG', quality=quality)
    buf.seek(0)
    with Image.open(buf) as im:
        return im.convert('RGB').copy()


def _mae(a: Image.Image, b: Image.Image) -> float:
    if a.size != b.size:
        raise ValueError('Images must be aligned before comparing.')
    stats = ImageStat.Stat(ImageChops.difference(a.convert('RGB'), b.convert('RGB')))
    return round(sum(stats.mean) / 3, 4)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def gallery_test(source: Path, output: Path, options: Options | None = None) -> dict:
    """Compare marked/unmarked pairs under identical lossy transforms.

    The residual is *not* a security rating: it is only a pixel-difference proxy.
    """
    source, output = Path(source).resolve(), Path(output).resolve()
    options = options or Options()
    options.validate()
    if not source.is_file():
        raise ValueError('Selecione uma foto existente.')
    if output == source.parent or output.is_relative_to(source.parent):
        raise ValueError('Salve o relatório fora da pasta dos originais.')
    output.mkdir(parents=True, exist_ok=True)
    marked_file = output / 'preview_marcada.jpg'
    create_preview(source, marked_file, options)
    with Image.open(source) as image:
        clean = ImageOps.exif_transpose(image).convert('RGB')
        clean.thumbnail((options.max_size, options.max_size), Image.Resampling.LANCZOS)
    with Image.open(marked_file) as image:
        marked = image.convert('RGB').copy()
    original_hash = _sha256(source)
    baseline = _mae(clean, marked)
    transforms = [
        ('jpeg_85', 1.0, 85),
        ('jpeg_60', 1.0, 60),
        ('jpeg_35', 1.0, 35),
        ('resize_75_jpeg_70', .75, 70),
        ('resize_50_jpeg_60', .5, 60),
    ]
    rows = []
    for name, scale, quality in transforms:
        size = (max(1, round(marked.width * scale)), max(1, round(marked.height * scale)))
        clean_small = clean.resize(size, Image.Resampling.LANCZOS) if scale != 1 else clean
        marked_small = marked.resize(size, Image.Resampling.LANCZOS) if scale != 1 else marked
        # Compare outputs after the SAME transform; this avoids conflating resizing with watermark loss.
        clean_processed = _jpg(clean_small, quality)
        marked_processed = _jpg(marked_small, quality)
        name_file = name + '.jpg'
        marked_processed.save(output / name_file, 'JPEG', quality=95)
        residual = _mae(clean_processed, marked_processed)
        rows.append({'variant': name, 'file': name_file, 'dimensions': list(size),
                     'difference_from_paired_clean_mae_0_255': residual,
                     'relative_to_pretransform_difference': round(residual / baseline, 4) if baseline else None})
    if _sha256(source) != original_hash:
        raise RuntimeError('A foto original mudou durante a operação. Não utilize este resultado.')
    results = {
        'version': '0.7.0', 'source': source.name, 'source_sha256': original_hash,
        'baseline_difference_mae_0_255': baseline, 'variants': rows,
        'caution': 'Valores indicam somente diferença média entre imagens marcadas e limpas após transformações idênticas. Não indicam legibilidade, eficácia comercial ou resistência contra remoção de marca d’água por IA.',
        'source_preserved': True,
    }
    (output / 'gallery-report.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf8')
    trs = ''.join(f'<tr><td>{html.escape(row["variant"])}</td><td>{row["dimensions"][0]} × {row["dimensions"][1]}</td><td>{row["difference_from_paired_clean_mae_0_255"]:.2f}</td><td><a href="{row["file"]}">Ver prévia</a></td></tr>' for row in rows)
    page = f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Markveil • Gallery Lab</title><style>body{{font:16px system-ui;background:#0e1726;color:#edf2fa;margin:36px auto;max-width:920px;padding:0 18px}}a{{color:#8ebcff}}img{{max-width:100%;border-radius:12px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #354359}}.note{{background:#273346;padding:16px;border-radius:10px}}</style><h1>Gallery Lab · Markveil v0.7</h1><p>Foto: {html.escape(source.name)}</p><p class="note"><strong>Aviso:</strong> {html.escape(results['caution'])}</p><h2>Prévia gerada</h2><img src="preview_marcada.jpg" alt="Prévia com marca"><p>Diferença média antes das transformações: {baseline:.2f} / 255.</p><h2>Simulações de publicação</h2><table><thead><tr><th>Transformação</th><th>Dimensões</th><th>Diferença (0–255)</th><th>Arquivo</th></tr></thead><tbody>{trs}</tbody></table><p>Os originais não são incluídos no relatório.</p></html>'''
    (output / 'index.html').write_text(page, encoding='utf8')
    return results
