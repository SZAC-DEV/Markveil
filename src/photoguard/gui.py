"""Desktop UI; processing runs in worker thread so GUI remains responsive."""
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import tempfile
from .comparison import compare_profiles
from .benchmark import benchmark_photo
from .gallery_lab import gallery_test
from .attack_lab import attack_test
from .core import create_preview
from .core import Options, process_directory

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PhotoGuard Studio — proteção de prévias')
        self.geometry('980x820')
        self.minsize(800, 650)
        self.configure(bg='#0b1220')
        self.q=queue.Queue()
        self.source=tk.StringVar()
        self.target=tk.StringVar()
        self.mark=tk.StringVar(value='PRÉVIA • NÃO COMPRADA')
        self.size=tk.StringVar(value='1100')
        self.opacity=tk.StringVar(value='130')
        self.density=tk.StringVar(value='4')
        self.grid_on=tk.BooleanVar(value=True)
        self.logo=tk.StringVar()
        self.logo_scale=tk.StringVar(value='32')
        self.protection=tk.StringVar(value='adaptive')
        style=ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#101c30')
        style.configure('TLabel', background='#101c30', foreground='#e5ecf8', font=('Segoe UI',10))
        style.configure('TButton', font=('Segoe UI',10,'bold'), padding=(14,10), borderwidth=0,
                        background='#2563eb', foreground='#ffffff')
        style.map('TButton',background=[('active','#1d4ed8'),('disabled','#334155')])
        style.configure('TCheckbutton', background='#101c30', foreground='#e5ecf8',font=('Segoe UI',10))
        style.configure('TEntry', padding=8, fieldbackground='#f1f5f9', foreground='#0f172a')
        style.configure('TCombobox',padding=7)
        style.configure('TNotebook',background='#0b1220',borderwidth=0)
        style.configure('TNotebook.Tab',font=('Segoe UI',10,'bold'),padding=(20,10),background='#162740',foreground='#cbd5e1')
        style.map('TNotebook.Tab',background=[('selected','#2563eb')],foreground=[('selected','white')])

        header=tk.Frame(self,bg='#0b1220',padx=26,pady=15)
        header.pack(fill='x')
        tk.Label(header,text='◆',font=('Segoe UI',26,'bold'),fg='#60a5fa',bg='#0b1220').pack(side='left',padx=(0,12))
        hero=tk.Frame(header,bg='#0b1220')
        hero.pack(side='left')
        tk.Label(hero,text='PhotoGuard',font=('Segoe UI',25,'bold'),fg='#f8fafc',bg='#0b1220').pack(anchor='w')
        tk.Label(hero,text='STUDIO  /  PRÉVIAS PROTEGIDAS  /  PROCESSAMENTO LOCAL',font=('Segoe UI',9,'bold'),fg='#7c9abf',bg='#0b1220').pack(anchor='w')
        tk.Label(header,text='v0.8  •  OPEN SOURCE',font=('Segoe UI',9,'bold'),fg='#93c5fd',bg='#0b1220').pack(side='right')

        notebook=ttk.Notebook(self)
        notebook.pack(fill='both',expand=True,padx=24,pady=(0,16))
        protect=ttk.Frame(notebook,padding=20)
        labs=ttk.Frame(notebook,padding=20)
        notebook.add(protect,text='  PROTEGER FOTOS  ')
        notebook.add(labs,text='  LABORATÓRIOS  ')
        ttk.Label(protect,text='Arquivos e publicação',font=('Segoe UI',15,'bold'),foreground='#93c5fd').pack(anchor='w',pady=(0,9))
        self._folder(protect,'Pasta com fotografias originais',self.source)
        self._folder(protect,'Pasta de saída das prévias protegidas',self.target)
        ttk.Label(protect,text='Texto da marca d’água').pack(anchor='w',pady=(12,4))
        ttk.Entry(protect,textvariable=self.mark).pack(fill='x')
        line=ttk.Frame(protect)
        line.pack(fill='x',pady=11)
        for col,(label,var) in enumerate([('Resolução máxima (px)',self.size),('Opacidade (30–240)',self.opacity),('Densidade (2–9)',self.density)]):
            part=ttk.Frame(line)
            part.grid(row=0,column=col,sticky='ew',padx=(0,12))
            ttk.Label(part,text=label).pack(anchor='w')
            ttk.Entry(part,textvariable=var).pack(fill='x',pady=3)
            line.columnconfigure(col,weight=1)
        self._file(protect,'Logotipo em PNG transparente (opcional)',self.logo)
        line2=ttk.Frame(protect)
        line2.pack(fill='x',pady=(12,8))
        left=ttk.Frame(line2);left.pack(side='left',fill='x',expand=True,padx=(0,12))
        ttk.Label(left,text='Perfil de proteção').pack(anchor='w')
        ttk.Combobox(left,textvariable=self.protection,values=['classic','adaptive','strong'],state='readonly').pack(fill='x',pady=3)
        right=ttk.Frame(line2);right.pack(side='left')
        ttk.Label(right,text='Largura do logo (%)').pack(anchor='w')
        ttk.Entry(right,textvariable=self.logo_scale,width=16).pack(pady=3)
        ttk.Checkbutton(protect,text='Aplicar grade geométrica adicional',variable=self.grid_on).pack(anchor='w',pady=5)
        actions=ttk.Frame(protect)
        actions.pack(fill='x',pady=(14,5))
        ttk.Button(actions,text='VISUALIZAR PRÉVIA',command=self.preview).pack(side='left',fill='x',expand=True,padx=(0,6))
        ttk.Button(actions,text='COMPARAR PERFIS',command=self.compare).pack(side='left',fill='x',expand=True)
        self.go=ttk.Button(protect,text='GERAR PRÉVIAS PROTEGIDAS →',command=self.start)
        self.go.pack(fill='x',pady=(12,8))

        ttk.Label(labs,text='Ferramentas de avaliação',font=('Segoe UI',16,'bold'),foreground='#93c5fd').pack(anchor='w',pady=(3,8))
        ttk.Label(labs,text='Selecione primeiro a pasta com imagens na aba Proteger fotos.').pack(anchor='w',pady=(0,18))
        for title,desc,action in [
            ('SIMULAR GALERIAS','Compressão JPEG e redimensionamento • não avalia remoção por IA',self.gallery_lab),
            ('TESTAR COMPRESSÃO','Avaliação técnica e relatório HTML',self.evaluate),
            ('IMPORTAR RESULTADO DE IA','Compare com uma fotografia editada por ferramenta externa',self.external_attack),
            ('PROTEÇÃO ADVERSARIAL EXPERIMENTAL','Exige PyTorch e modelo VAE opcional; eficácia não comprovada',self.adversarial_preview),
        ]:
            panel=ttk.Frame(labs,padding=(8,8));panel.pack(fill='x',pady=6)
            ttk.Label(panel,text=desc,foreground='#9fb4d0').pack(anchor='w',pady=(0,5))
            ttk.Button(panel,text=title,command=action).pack(fill='x')

        footer=tk.Frame(self,bg='#0b1220',padx=24,pady=5)
        footer.pack(fill='x',side='bottom')
        tk.Label(footer,text='ATIVIDADE  /  REGISTRO',font=('Segoe UI',9,'bold'),fg='#7c9abf',bg='#0b1220').pack(anchor='w')
        self.log=tk.Text(footer,height=4,bg='#060e1c',fg='#c7d8f1',insertbackground='white',relief='flat',font=('Consolas',9),padx=10,pady=8)
        self.log.pack(fill='x',pady=(4,8))
        self.log.insert('end','Pronto para gerar prévias. Seus originais serão preservados.\n')
        self.after(120,self.poll)

    def _folder(self,frame,label,var):
        ttk.Label(frame,text=label).pack(anchor='w',pady=(6,3))
        line=ttk.Frame(frame)
        line.pack(fill='x')
        ttk.Entry(line,textvariable=var).pack(side='left',fill='x',expand=True)
        ttk.Button(line,text='Procurar',command=lambda:var.set(filedialog.askdirectory() or var.get())).pack(side='right',padx=(7,0))

    def _file(self,frame,label,var):
        ttk.Label(frame,text=label).pack(anchor='w',pady=(8,3))
        line=ttk.Frame(frame)
        line.pack(fill='x')
        ttk.Entry(line,textvariable=var).pack(side='left',fill='x',expand=True)
        ttk.Button(line,text='PNG...',command=lambda:var.set(filedialog.askopenfilename(filetypes=[('PNG','*.png')]) or var.get())).pack(side='right',padx=(7,0))

    def _build_processing_options(self):
        opts=Options(text=self.mark.get(),max_size=int(self.size.get()),opacity=int(self.opacity.get()),density=int(self.density.get()),grid=self.grid_on.get(),logo_path=self.logo.get(),logo_scale=int(self.logo_scale.get()),protection=self.protection.get())
        opts.validate()
        return opts

    def preview(self):
        try:
            options=self._build_processing_options()
            folder=Path(self.source.get())
            from .core import SUPPORTED
            photos=sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED) if folder.is_dir() else []
            if not photos: raise ValueError('Escolha uma pasta com pelo menos uma fotografia.')
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'preview.jpg'
                create_preview(photos[0],path,options)
                with Image.open(path) as im:
                    img=im.copy()
            img.thumbnail((960,680),Image.Resampling.LANCZOS)
            dialog=tk.Toplevel(self)
            dialog.title('PhotoGuard · Visualização: '+photos[0].name)
            photo=ImageTk.PhotoImage(img,master=dialog)
            label=tk.Label(dialog,image=photo,bg='#101827')
            label.image=photo
            label.pack(padx=10,pady=10)
        except (ValueError,OSError,TypeError) as e:
            messagebox.showerror('Prévia indisponível',str(e))

    def compare(self):
        try:
            options=self._build_processing_options()
            folder=Path(self.source.get())
            from .core import SUPPORTED
            photos=sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED) if folder.is_dir() else []
            if not photos:
                raise ValueError('Escolha uma pasta com fotografias.')
            path=filedialog.asksaveasfilename(title='Salvar comparação',defaultextension='.jpg',filetypes=[('JPEG','*.jpg')],initialfile='photoguard-comparacao.jpg')
            if path:
                compare_profiles(photos[0],Path(path),options)
                messagebox.showinfo('Comparação salva',f'Comparação gerada em: {path}')
        except (ValueError,OSError,TypeError) as exc:
            messagebox.showerror('Falha na comparação',str(exc))

    def evaluate(self):
        try:
            options=self._build_processing_options()
            folder=Path(self.source.get())
            from .core import SUPPORTED
            photos=sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED) if folder.is_dir() else []
            if not photos:
                raise ValueError('Escolha uma pasta de entrada com fotos.')
            target=filedialog.askdirectory(title='Pasta para relatório (fora dos originais)')
            if not target:
                return
            result=benchmark_photo(photos[0],Path(target),options)
            messagebox.showinfo('Relatório salvo',f"Abra {Path(target) / 'index.html'} no navegador.\nAtenção: este teste não avalia remoção por IA.")
        except (ValueError,OSError,TypeError) as exc:
            messagebox.showerror('Falha na avaliação',str(exc))

    def gallery_lab(self):
        try:
            opts = self._build_processing_options()
            from .core import SUPPORTED
            folder = Path(self.source.get())
            photos = sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED) if folder.is_dir() else []
            if not photos:
                raise ValueError('Selecione uma pasta com fotos.')
            target = filedialog.askdirectory(title='Pasta para o relatório (fora dos originais)')
            if not target:
                return
            import webbrowser
            result = gallery_test(photos[0], Path(target), opts)
            webbrowser.open((Path(target) / 'index.html').resolve().as_uri())
            messagebox.showinfo('Gallery Lab', 'Relatório gerado. Não comprova resistência à IA.')
        except (ValueError, OSError, RuntimeError) as exc:
            messagebox.showerror('Gallery Lab', str(exc))

    def external_attack(self):
        try:
            options=self._build_processing_options()
            folder=Path(self.source.get())
            from .core import SUPPORTED
            photos=sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED) if folder.is_dir() else []
            if not photos: raise ValueError('Selecione uma pasta com fotos originais.')
            attacked=filedialog.askopenfilename(title='Foto após remoção por IA',filetypes=[('Imagens','*.jpg *.jpeg *.png *.webp')])
            if not attacked: return
            target=filedialog.askdirectory(title='Pasta do relatório (fora dos originais)')
            if not target:return
            attack_test(photos[0],Path(target),options,attacked=Path(attacked))
            messagebox.showinfo('Relatório criado',f"Abra {Path(target) / 'attack_report.html'} no navegador.\nMétricas de pixels não comprovam segurança.")
        except (ValueError,OSError,RuntimeError,TypeError) as exc:
            messagebox.showerror('Falha no laboratório',str(exc))

    def adversarial_preview(self):
        """Select an already-watermarked preview; use optional local VAE model."""
        source=filedialog.askopenfilename(title='Escolha uma PRÉVIA já marcada (não o original)',filetypes=[('Imagens','*.jpg *.jpeg *.png *.webp')])
        if not source:return
        target=filedialog.asksaveasfilename(title='Salvar proteção experimental como PNG',defaultextension='.png',filetypes=[('PNG','*.png')],initialfile='previa-adversarial.png')
        if not target:return
        if Path(source).resolve()==Path(target).resolve():
            messagebox.showerror('Erro','Não é permitido sobrescrever o arquivo de entrada.')
            return
        if not messagebox.askyesno('Recurso experimental','Usa PyTorch e um modelo VAE local (download inicial pode ser grande).\nNão garante impedir remoção por IA.\nExecutar?'):
            return
        self.log.insert('end','Iniciando proteção experimental...\n')
        def work():
            try:
                from .adversarial import protect_preview
                result=protect_preview(Path(source),Path(target))
                self.q.put(('done',f"PNG experimental salvo: {result['output']}"))
            except Exception as exc:
                self.q.put(('error',f'Proteção adversarial: {exc}'))
        threading.Thread(target=work,daemon=True).start()

    def start(self):
        try:
            options=self._build_processing_options()
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
