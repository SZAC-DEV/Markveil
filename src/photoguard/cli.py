import argparse
import json
from .comparison import compare_profiles
from .benchmark import benchmark_photo
from .attack_lab import attack_test
from pathlib import Path
from .core import Options, process_directory

def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'gallery-test':
        from .gallery_lab import gallery_test
        lab = argparse.ArgumentParser(description='Simula compressão e redimensionamento de galerias (NÃO testa remoção por IA)')
        lab.add_argument('command', choices=['gallery-test'])
        lab.add_argument('photo', type=Path)
        lab.add_argument('output', type=Path)
        lab.add_argument('--text', default='PRÉVIA • NÃO COMPRADA')
        lab.add_argument('--logo', default='')
        lab.add_argument('--protection', choices=['classic','adaptive','strong'], default='adaptive')
        args = lab.parse_args()
        try:
            report = gallery_test(args.photo, args.output, Options(text=args.text, logo_path=args.logo, protection=args.protection))
        except (ValueError, OSError, RuntimeError) as exc:
            lab.error(str(exc))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    if len(sys.argv) > 1 and sys.argv[1] == 'attack-test':
        check=argparse.ArgumentParser(description='Laboratório: ataque externo ou inpainting clássico local')
        check.add_argument('command', choices=['attack-test'])
        check.add_argument('photo', type=Path)
        check.add_argument('output', type=Path)
        choice=check.add_mutually_exclusive_group(required=True)
        choice.add_argument('--attacked', type=Path, help='Imagem após processamento por IA externa')
        choice.add_argument('--local-inpaint',action='store_true',help='Inpainting clássico OpenCV, NÃO IA generativa')
        check.add_argument('--mask',type=Path,help='Máscara do ataque em escala de cinza, branco=região removida')
        check.add_argument('--text',default='PRÉVIA • NÃO COMPRADA')
        check.add_argument('--logo',default='')
        args=check.parse_args()
        try:
            result=attack_test(args.photo,args.output,Options(text=args.text,logo_path=args.logo),args.attacked,args.local_inpaint,args.mask)
        except (ValueError,OSError,RuntimeError) as exc:
            check.error(str(exc))
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return
    if len(sys.argv) > 1 and sys.argv[1] == 'compare':
        parser_compare=argparse.ArgumentParser(description='Comparação de três perfis de proteção')
        parser_compare.add_argument('command',choices=['compare'])
        parser_compare.add_argument('photo',type=Path)
        parser_compare.add_argument('output',type=Path)
        parser_compare.add_argument('--logo',default='')
        args=parser_compare.parse_args()
        output=compare_profiles(args.photo,args.output,Options(logo_path=args.logo))
        print(f'Comparação salva em {output}')
        return
    if len(sys.argv) > 1 and sys.argv[1] == 'benchmark':
        check=argparse.ArgumentParser(description='Avaliação local de compressão e redimensionamento (não IA)')
        check.add_argument('command', choices=['benchmark'])
        check.add_argument('photo', type=Path)
        check.add_argument('output', type=Path)
        check.add_argument('--logo', default='')
        check.add_argument('--text', default='PRÉVIA • NÃO COMPRADA')
        args=check.parse_args()
        result=benchmark_photo(args.photo,args.output,Options(text=args.text,logo_path=args.logo))
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return
    parser=argparse.ArgumentParser(description='PhotoGuard: prévias protegidas para fotógrafos')
    parser.add_argument('input',type=Path,help='Pasta com originais')
    parser.add_argument('output',type=Path,help='Pasta diferente, para prévias')
    parser.add_argument('--text',default='PRÉVIA • NÃO COMPRADA')
    parser.add_argument('--size',type=int,default=1100)
    parser.add_argument('--opacity',type=int,default=130)
    parser.add_argument('--density',type=int,default=4)
    parser.add_argument('--quality',type=int,default=76)
    parser.add_argument('--logo',default='',help='PNG transparente de marca personalizada')
    parser.add_argument('--logo-scale',type=int,default=32,help='Largura do PNG em %% da prévia')
    parser.add_argument('--protection', choices=['classic','adaptive','strong'], default='adaptive')
    parser.add_argument('--no-grid',action='store_true')
    args=parser.parse_args()
    opts=Options(text=args.text,max_size=args.size,opacity=args.opacity,density=args.density,quality=args.quality,grid=not args.no_grid,logo_path=args.logo,logo_scale=args.logo_scale,protection=args.protection)
    try:
        result=process_directory(args.input,args.output,opts,print)
    except (ValueError,OSError) as exc:
        parser.error(str(exc))
    print(f"Concluído: {len(result['images'])} prévias, {len(result['errors'])} erros.")
    if result['errors']: raise SystemExit(1)

if __name__=='__main__': main()
