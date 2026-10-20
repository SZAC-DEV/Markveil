"""Reproducible *non-AI* preview robustness checks; not an AI-removal score."""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageChops, ImageOps, ImageStat
from .core import Options, create_preview
import io, json, tempfile, html


def _difference(a: Image.Image, b: Image.Image) -> float:
    """Normalized average absolute RGB difference [0, 1]."""
    if a.size != b.size:
        b = b.resize(a.size, Image.Resampling.LANCZOS)
    stat = ImageStat.Stat(ImageChops.difference(a.convert('RGB'), b.convert('RGB')))
    return round(sum(stat.mean) / (3 * 255), 5)


def _jpeg(image: Image.Image, quality: int) -> Image.Image:
    stream = io.BytesIO()
    image.convert('RGB').save(stream, 'JPEG', quality=quality)
    stream.seek(0)
    with Image.open(stream) as reopened:
        return reopened.convert('RGB').copy()


def benchmark_photo(source: Path, destination: Path, options: Options | None = None) -> dict:
    """Create a local report and 3 preview variants; original is never modified.

    Distortion is not a watermark-removal attack and metrics must not be
    presented as proof of resistance to generative AI.
    """
    options = options or Options()
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise ValueError('Fotografia não encontrada.')
    if destination == source or destination.is_relative_to(source.parent):
        raise ValueError('Use uma pasta de relatório fora da pasta do original.')
    destination.mkdir(parents=True, exist_ok=True)
    marked = destination / 'marked.jpg'
    preview_data = create_preview(source, marked, options)
    with Image.open(source) as raw:
        clean = ImageOps.exif_transpose(raw).convert('RGB')
        clean.thumbnail((options.max_size, options.max_size), Image.Resampling.LANCZOS)
    with Image.open(marked) as marked_file:
        protected = marked_file.convert('RGB').copy()
    variants = {'jpeg_quality_45': _jpeg(protected, 45),
                'jpeg_quality_70': _jpeg(protected, 70)}
    w, h = protected.size
    reduced = protected.resize((max(1,w//2), max(1,h//2)), Image.Resampling.LANCZOS)
    variants['resize_50_percent'] = reduced
    measured = {}
    baseline = _difference(protected, clean)
    for name, image in variants.items():
        filename = name + '.jpg'
        image.save(destination / filename, 'JPEG', quality=88)
        if image.size != protected.size:
            resized_clean = clean.resize(image.size, Image.Resampling.LANCZOS)
        else:
            resized_clean = clean
        measured[name] = {
            'file': filename,
            'image_change_from_marked': _difference(image, protected),
            'difference_from_unmarked': _difference(image, resized_clean),
        }
    result = {
        'version': '0.3.0', 'source_name': source.name,
        'source_sha256': preview_data['source_sha256'],
        'baseline_difference_from_unmarked': baseline,
        'variants': measured,
        'limitations': 'Mede diferenças de pixels sob compressão e redimensionamento. Não mede legibilidade da marca nem resistência à remoção por IA.'
    }
    (destination / 'benchmark.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    table = ''.join(f'<tr><td>{html.escape(name)}</td><td>{metrics["image_change_from_marked"]:.3f}</td><td>{metrics["difference_from_unmarked"]:.3f}</td><td><a href="{metrics["file"]}">Ver imagem</a></td></tr>' for name, metrics in measured.items())
    page = f'''<!DOCTYPE html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Markveil • Avaliação</title><style>body{{font:16px system-ui;background:#0b1220;color:#eaf1ff;max-width:900px;margin:50px auto;padding:0 24px}}h1{{color:#79b3ff}}table{{border-collapse:collapse;width:100%}}td,th{{padding:13px;border-bottom:1px solid #344155;text-align:left}}a{{color:#8ec5ff}}.warning{{background:#253149;padding:16px;border-radius:9px}}img{{max-width:100%;border-radius:9px}}</style><h1>Markveil • Avaliação local</h1><p>Arquivo: {html.escape(source.name)}</p><div class="warning"><strong>Aviso:</strong> este benchmark não simula remoção com IA. Alterações de pixels não comprovam segurança.</div><h2>Prévia protegida</h2><img src="marked.jpg" alt="Prévia"><p>Diferença média vs. versão sem marca: {baseline:.3f} (escala de 0 a 1).</p><h2>Transformações</h2><table><tr><th>Teste</th><th>Mudança vs. prévia</th><th>Diferença vs. original reduzido</th><th>Arquivo</th></tr>{table}</table><p>Valores maiores indicam mais diferença de pixels, não necessariamente melhor marca d'água.</p></html>'''
    (destination / 'index.html').write_text(page, encoding='utf-8')
    return result
