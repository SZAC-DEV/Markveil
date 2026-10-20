"""Optional, best-effort machine telemetry. Not GPU usage attributable to this app."""
import shutil
import subprocess

def sample_resources():
    try:
        import psutil
        cpu=psutil.cpu_percent(interval=None)
        mem=psutil.virtual_memory()
        ram=f'{mem.used/1024**3:.1f}/{mem.total/1024**3:.1f} GB'
        proc=f'{psutil.Process().memory_info().rss/1024**2:.0f} MB'
    except ImportError:
        cpu=None;ram='indisponível (psutil)';proc='—'
    gpu='GPU: indisponível'
    if shutil.which('nvidia-smi'):
        try:
            result=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,memory.total','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=2,check=True)
            first=result.stdout.strip().splitlines()[0].split(',')
            util,used,total=[item.strip() for item in first[:3]]
            gpu=f'GPU NVIDIA: {util}% · VRAM {used}/{total} MiB'
        except (OSError,subprocess.SubprocessError,IndexError,ValueError):pass
    cpu_text=f'{cpu:.0f}%' if cpu is not None else '—'
    return {'cpu_percent':cpu,'label':f'CPU sistema: {cpu_text}  ·  RAM sistema: {ram}  ·  App: {proc}  ·  {gpu}', 'gpu':gpu}
