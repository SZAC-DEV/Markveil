"""Experimental gradient-based perturbation of a watermarked PREVIEW.

Research prototype inspired by the MadryLab paper, NOT a port or validation
of their code/attack. Specifically maximizes VAE encoder latent deviation;
performance against actual watermark removal models is unverified.
"""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageOps

DEFAULT_MODEL = 'stabilityai/sd-vae-ft-mse'

@dataclass(frozen=True)
class AdversarialConfig:
    epsilon: int = 6  # maximum pixel change in 0..255
    steps: int = 20
    step_size: float = 1.0  # pixel units
    size: int = 512
    model: str = DEFAULT_MODEL
    device: str = 'auto'

    def validate(self):
        if not 1 <= self.epsilon <= 16: raise ValueError('epsilon deve estar entre 1 e 16.')
        if not 1 <= self.steps <= 150: raise ValueError('steps deve estar entre 1 e 150.')
        if not 0 < self.step_size <= 10: raise ValueError('step_size deve estar entre 0 e 10.')
        if not 128 <= self.size <= 1024 or self.size % 8: raise ValueError('size deve ser múltiplo de 8, entre 128 e 1024.')
        if self.device not in ('auto','cpu','cuda'): raise ValueError('device deve ser auto, cpu ou cuda.')
        if not self.model.strip(): raise ValueError('Informe o modelo VAE.')


def protect_preview(source: Path, output: Path, config: AdversarialConfig = AdversarialConfig()):
    """Generate adversarial *preview* as PNG without touching source.

    Existing watermarks in source remain. This function must not be used on
    sale-quality originals: it intentionally makes image quality worse.
    """
    config.validate()
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output: raise ValueError('O resultado não pode sobrescrever a entrada.')
    if not source.is_file(): raise FileNotFoundError(source)
    if output.suffix.lower() != '.png': raise ValueError('Use saída PNG: JPEG destrói parte das perturbações.')
    try:
        import torch
        from diffusers import AutoencoderKL
    except ImportError as exc:
        raise RuntimeError('Instale suporte opcional: python -m pip install -e ".[adversarial]"') from exc
    device = 'cuda' if config.device == 'auto' and torch.cuda.is_available() else ('cpu' if config.device == 'auto' else config.device)
    if device == 'cuda' and not torch.cuda.is_available(): raise RuntimeError('CUDA não disponível. Escolha CPU ou configure PyTorch com CUDA.')
    # Model is downloaded by Hugging Face the first time; user must accept its license.
    vae = AutoencoderKL.from_pretrained(config.model)
    vae.to(device).eval()
    vae.requires_grad_(False)
    with Image.open(source) as im:
        image = ImageOps.exif_transpose(im).convert('RGB')
        image.thumbnail((config.size,config.size),Image.Resampling.LANCZOS)
        # VAE requires spatial size multiple of 8. Cropping is deliberate, documented.
        image = image.crop((0,0,max(8,image.width//8*8),max(8,image.height//8*8)))
    import numpy as np
    array = np.asarray(image,dtype='float32').copy()/255.
    base = torch.from_numpy(array).permute(2,0,1).unsqueeze(0).to(device)
    bound = config.epsilon / 255.
    delta = (torch.rand_like(base)*2-1) * (bound * 0.25)  # nonzero initial point for squared-distance objective
    with torch.no_grad():
        original_latents = vae.encode(base*2-1).latent_dist.mean.detach()
    for _ in range(config.steps):
        delta = delta.detach().requires_grad_(True)
        perturbed = (base+delta).clamp(0,1)
        latents = vae.encode(perturbed*2-1).latent_dist.mean
        objective = (latents-original_latents).square().mean()
        gradient = torch.autograd.grad(objective, delta)[0]
        with torch.no_grad():
            delta = (delta + (config.step_size/255.)*gradient.sign()).clamp(-bound,bound)
            delta = ((base+delta).clamp(0,1)-base).detach()
    final = ((base+delta).clamp(0,1)*255).round().byte().squeeze(0).permute(1,2,0).cpu().numpy()
    output.parent.mkdir(parents=True,exist_ok=True)
    # Saving PNG avoids re-compression and does not propagate EXIF/GPS.
    Image.fromarray(final,'RGB').save(output,format='PNG')
    return {'source':str(source),'output':str(output),'model':config.model,'epsilon':config.epsilon,
            'steps':config.steps,'device':device,'width':image.width,'height':image.height,
            'warning':'Experimental VAE perturbation; not verified against watermark removal AI.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description='Markveil: proteção adversarial experimental para prévias já marcadas')
    parser.add_argument('preview',type=Path,help='Arquivo de PRÉVIA já marcado, nunca o original')
    parser.add_argument('output',type=Path,help='Arquivo de saída PNG')
    parser.add_argument('--epsilon',type=int,default=6)
    parser.add_argument('--steps',type=int,default=20)
    parser.add_argument('--size',type=int,default=512)
    parser.add_argument('--step-size',type=float,default=1.)
    parser.add_argument('--model',default=DEFAULT_MODEL)
    parser.add_argument('--device',choices=['auto','cuda','cpu'],default='auto')
    args=parser.parse_args(argv)
    result=protect_preview(args.preview,args.output,AdversarialConfig(args.epsilon,args.steps,args.step_size,args.size,args.model,args.device))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
