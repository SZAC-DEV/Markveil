import argparse
import json
from .benchmark import benchmark_photo
from pathlib import Path
from .core import Options, process_directory

def main():
    import sys
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
    parser.add_argument('--no-grid',action='store_true')
    args=parser.parse_args()
    opts=Options(text=args.text,max_size=args.size,opacity=args.opacity,density=args.density,quality=args.quality,grid=not args.no_grid,logo_path=args.logo,logo_scale=args.logo_scale)
    try:
        result=process_directory(args.input,args.output,opts,print)
    except (ValueError,OSError) as exc:
        parser.error(str(exc))
    print(f"Concluído: {len(result['images'])} prévias, {len(result['errors'])} erros.")
    if result['errors']: raise SystemExit(1)

if __name__=='__main__': main()
