import argparse
from pathlib import Path
from .core import Options, process_directory

def main():
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
