"""Offline attack lab. Never claims to measure all generative watermark removers."""
from __future__ import annotations
import html
import json
import math
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat
from .core import Options, create_preview, _sha256


def _rgb(path: Path, size=None):
    with Image.open(path) as im:
        result = ImageOps.exif_transpose(im).convert('RGB')
        if size is not None:
            result = result.resize(size, Image.Resampling.LANCZOS)
        return result


def _mae(a, b):
    if b.size != a.size: b=b.resize(a.size, Image.Resampling.LANCZOS)
    diff=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
    return sum(ImageStat.Stat(diff).mean)/(3*255)


def _psnr(a,b):
    if b.size != a.size: b=b.resize(a.size,Image.Resampling.LANCZOS)
    stat=ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB')))
    mse=sum(stat.sum2)/(3*a.width*a.height)
    return None if mse==0 else round(10*math.log10(255*255/mse),3)


def _mask_from_difference(clean, marked, threshold=23):
    """Mask is approximate, not watermark ground truth (JPEG adds artifacts)."""
    diff=ImageChops.difference(clean,marked).convert('L')
    mask=diff.point(lambda p: 255 if p>=threshold else 0)
    return mask.filter(ImageFilter.MaxFilter(5))


def _local_inpaint(marked, mask, radius=3):
    """Optional OpenCV classical inpainting baseline, not a generative AI model."""
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError('Ataque local requer: pip install photoguard-open[attack]') from exc
    rgb=np.asarray(marked.convert('RGB'))
    bgr=cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    result=cv2.inpaint(bgr,np.asarray(mask.convert('L')),radius,cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(result,cv2.COLOR_BGR2RGB))


def attack_test(source: Path, destination: Path, options: Options|None=None,
                attacked: Path|None=None, local_inpaint=False, mask: Path|None=None):
    """Compare marked preview with an externally attacked image or classical inpainting.

    An external image may be produced by any AI editor; no model download or API is needed.
    Attacked and original are never overwritten. All scores are pixel similarity, not
    proof of resistance, nor proof that an image still carries readable ownership marks.
    """
    source=Path(source).resolve()
    destination=Path(destination).resolve()
    if not source.is_file(): raise ValueError('Original não encontrado')
    if destination == source.parent or destination.is_relative_to(source.parent):
        raise ValueError('Relatório precisa ficar fora da pasta do original')
    if attacked is None and not local_inpaint:
        raise ValueError('Escolha --attacked ou --local-inpaint')
    if attacked is not None and local_inpaint:
        raise ValueError('Escolha apenas um modo de ataque')
    if attacked is not None and not Path(attacked).is_file():
        raise ValueError('Imagem atacada não encontrada')
    if mask is not None and not Path(mask).is_file():
        raise ValueError('Máscara não encontrada')
    destination.mkdir(parents=True,exist_ok=True)
    marked_path=destination/'marked.jpg'
    opts=options or Options()
    create_preview(source,marked_path,opts)
    marked=_rgb(marked_path)
    clean=_rgb(source,marked.size)
    if mask is None:
        candidate_mask=_mask_from_difference(clean,marked)
        mask_kind='estimated_from_pixels'
    else:
        with Image.open(mask) as supplied:
            candidate_mask=supplied.convert('L').resize(marked.size,Image.Resampling.NEAREST)
        mask_kind='supplied'
    candidate_mask.save(destination/'attack_mask.png')
    if local_inpaint:
        result=_local_inpaint(marked,candidate_mask)
        mode='opencv_telea_non_ai'
    else:
        result=_rgb(Path(attacked),marked.size)
        mode='external_attack_image'
    result.save(destination/'attacked.jpg',quality=95)
    baseline=_mae(marked,clean)
    residual=_mae(result,clean)
    change=_mae(result,marked)
    values={
        'version':'0.4.0', 'mode':mode,'source_name':source.name,
        'source_sha256':_sha256(source), 'mask_kind':mask_kind,
        'mask_coverage_fraction':round(ImageStat.Stat(candidate_mask).mean[0]/255,5),
        'baseline_mae_to_original':round(baseline,5),
        'attacked_mae_to_original':round(residual,5),
        'change_from_marked_mae':round(change,5),
        'pixel_error_reduction_percent':round(100*(baseline-residual)/baseline,2) if baseline else None,
        'attacked_psnr_to_original_db':_psnr(result,clean),
        'limitations':('Comparação de pixels, não avaliação de legibilidade, atribuição, ou resistência geral à IA. '
                       'Máscara estimada mistura marca, compressão e alterações da prévia. '
                       'Ataques de IA externos exigem exportar e importar manualmente sua imagem. '
                       'Resultados não são comparáveis quando o atacante usa outro enquadramento ou edição.'),
    }
    (destination/'attack_report.json').write_text(json.dumps(values,ensure_ascii=False,indent=2),encoding='utf-8')
    items=''.join(f'<tr><th>{html.escape(k)}</th><td>{html.escape(str(v))}</td></tr>' for k,v in values.items())
    report=f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PhotoGuard • Laboratório</title><style>body{{font:15px system-ui;background:#0d1423;color:#ecf2ff;max-width:1000px;margin:36px auto;padding:0 20px}}h1{{color:#8fc0ff}}.images{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}}img{{width:100%;border-radius:10px}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;border-bottom:1px solid #384659;text-align:left;overflow-wrap:anywhere}}.note{{padding:14px;background:#253247;border-radius:9px}}</style><h1>PhotoGuard • Laboratório de ataques</h1><p class="note">Este relatório NÃO comprova proteção contra IA. {html.escape(values['limitations'])}</p><div class="images"><div><h2>Prévia marcada</h2><img src="marked.jpg"></div><div><h2>Resultado do ataque</h2><img src="attacked.jpg"></div><div><h2>Máscara utilizada</h2><img src="attack_mask.png"></div></div><h2>Métricas</h2><table>{items}</table></html>'''
    (destination/'attack_report.html').write_text(report,encoding='utf-8')
    return values
