"""Create a side-by-side local comparison of PhotoGuard protection presets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .core import create_preview, Options


def compare_profiles(source: Path, destination: Path, options: Options) -> Path:
    source, destination = Path(source), Path(destination)
    if not source.is_file():
        raise ValueError('Selecione uma fotografia existente.')
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as temporary:
        imgs = []
        for mode in ('classic', 'adaptive', 'strong'):
            opts = Options(**{**vars(options), 'protection': mode})
            result = Path(temporary) / (mode + '.jpg')
            create_preview(source, result, opts)
            with Image.open(result) as im:
                sample = im.copy()
            sample.thumbnail((640, 480), Image.Resampling.LANCZOS)
            imgs.append((mode, sample))
        max_height = max(im.height for _, im in imgs)
        sheet = Image.new('RGB', (3 * 660 + 20, max_height + 84), '#101827')
        draw = ImageDraw.Draw(sheet)
        for idx, (name, im) in enumerate(imgs):
            x = 20 + idx * 660
            draw.text((x, 22), name.upper(), fill='white')
            sheet.paste(im, (x, 64))
        destination.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(destination, 'JPEG', quality=88)
    return destination
