from pathlib import Path
from PIL import Image
import pytest
from photoguard.core import Options, create_preview, process_directory

@pytest.mark.parametrize("profile", ["classic", "adaptive", "strong"])
def test_profile_generates_distinct_preview(tmp_path, profile):
    original = tmp_path / "original.png"
    Image.new("RGB", (440, 320), (130, 145, 160)).save(original)
    old_bytes = original.read_bytes()
    target = tmp_path / f"{profile}.jpg"
    create_preview(original, target, Options(protection=profile))
    assert target.exists() and target.stat().st_size > 500
    assert original.read_bytes() == old_bytes


def test_profiles_differ(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (450, 330), (130, 145, 160)).save(source)
    outputs = []
    for protection in ("classic", "adaptive", "strong"):
        dst = tmp_path / f"{protection}.jpg"
        create_preview(source, dst, Options(protection=protection))
        outputs.append(dst.read_bytes())
    assert len(set(outputs)) == 3


def test_invalid_profile():
    with pytest.raises(ValueError, match="Proteção inválida"):
        Options(protection="fake").validate()


def test_compare_profiles(tmp_path):
    from photoguard.comparison import compare_profiles
    source=tmp_path / 'src.jpg'
    Image.new('RGB',(500,350),(120,90,175)).save(source)
    output=tmp_path/'comparison.jpg'
    compare_profiles(source,output,Options())
    with Image.open(output) as im:
        assert im.width == 2000 and im.height > 100
