"""Desktop UI; processing runs in worker thread so GUI remains responsive."""
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from .core import Options, process_directory

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PhotoGuard · Preview Protection')
        self.geometry('760x560')
        self.configure(bg='#101827')
        self.q=queue.Queue()
        self.source=tk.StringVar()
        self.target=tk.StringVar()
        self.mark=tk.StringVar(value='PRÉVIA • NÃO COMPRADA')
        self.size=tk.StringVar(value='1100')
        self.opacity=tk.StringVar(value='130')
        self.density=tk.StringVar(value='4')
        self.grid_on=tk.BooleanVar(value=True)
        style=ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame',background='#101827')
        style.configure('TLabel',background='#101827',foreground='#eff6ff',font=('Segoe UI',10))
        style.configure('TButton',font=('Segoe UI',10),padding=8)
        style.configure('TCheckbutton',background='#101827',foreground='#eff6ff')
        style.configure('TEntry',padding=6)
        frame=ttk.Frame(self,padding=24)
        frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='PhotoGuard',font=('Segoe UI',25,'bold'),foreground='#7cb3ff').pack(anchor='w')
        ttk.Label(frame,text='Prévias marcadas. Originais preservados. Processamento 100% local.').pack(anchor='w',pady=(0,20))
        self._folder(frame,'Pasta com fotos originais',self.source)
        self._folder(frame,'Pasta para salvar prévias (fora dos originais)',self.target)
        ttk.Label(frame,text='Texto da marca d’água').pack(anchor='w',pady=(10,3))
        ttk.Entry(frame,textvariable=self.mark).pack(fill='x')
        opts=ttk.Frame(frame)
        opts.pack(fill='x',pady=12)
        for i,(title,var) in enumerate([('Tamanho máximo (px)',self.size),('Opacidade (30–240)',self.opacity),('Densidade (2–9)',self.density)]):
            part=ttk.Frame(opts)
            part.grid(row=0,column=i,sticky='ew',padx=(0,12))
            ttk.Label(part,text=title).pack(anchor='w')
            ttk.Entry(part,textvariable=var,width=17).pack(fill='x',pady=4)
            opts.columnconfigure(i,weight=1)
        ttk.Checkbutton(frame,text='Adicionar grade geométrica de proteção',variable=self.grid_on).pack(anchor='w')
        self.go=ttk.Button(frame,text='GERAR PRÉVIAS PROTEGIDAS',command=self.start)
        self.go.pack(fill='x',pady=(15,10))
        self.log=tk.Text(frame,height=7,bg='#0b1220',fg='#d7e7ff',insertbackground='white',relief='flat',font=('Consolas',9))
        self.log.pack(fill='both',expand=True)
        self.after(120,self.poll)

    def _folder(self,frame,label,var):
        ttk.Label(frame,text=label).pack(anchor='w',pady=(6,3))
        line=ttk.Frame(frame)
        line.pack(fill='x')
        ttk.Entry(line,textvariable=var).pack(side='left',fill='x',expand=True)
        ttk.Button(line,text='Procurar',command=lambda:var.set(filedialog.askdirectory() or var.get())).pack(side='right',padx=(7,0))

    def start(self):
        try:
            options=Options(text=self.mark.get(),max_size=int(self.size.get()),opacity=int(self.opacity.get()),density=int(self.density.get()),grid=self.grid_on.get())
            options.validate()
            inp=Path(self.source.get()).resolve()
            out=Path(self.target.get()).resolve()
            if not inp.is_dir() or inp==out or out.is_relative_to(inp):
                raise ValueError('Escolha uma pasta de entrada existente e uma pasta de saída fora dela.')
        except (ValueError,OSError) as e:
            messagebox.showerror('Configuração inválida',str(e))
            return
        self.go.configure(state='disabled')
        self.log.delete('1.0','end')
        def work():
            try:
                result=process_directory(inp,out,options,lambda line:self.q.put(('line',line)))
                self.q.put(('done',f"{len(result['images'])} prévias geradas, {len(result['errors'])} erros.\nRelatório em {out}"))
            except Exception as exc:
                self.q.put(('error',str(exc)))
        threading.Thread(target=work,daemon=True).start()

    def poll(self):
        try:
            while True:
                kind,msg=self.q.get_nowait()
                if kind=='line':
                    self.log.insert('end',msg+'\n')
                    self.log.see('end')
                else:
                    self.go.configure(state='normal')
                    if kind=='done': messagebox.showinfo('Concluído',msg)
                    else: messagebox.showerror('Erro',msg)
        except queue.Empty:
            pass
        self.after(120,self.poll)

def main():
    App().mainloop()

if __name__=='__main__': main()
