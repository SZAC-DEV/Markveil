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
        self.title('Markveil Studio — Image Protection')
        self.geometry('1140x850')
        self.minsize(960, 710)
        self.configure(bg='#0A101B')
        self.q=queue.Queue()
        self.source=tk.StringVar()
        self.target=tk.StringVar()
        self.mark=tk.StringVar(value='PREVIEW • NOT PURCHASED')
        self.size=tk.StringVar(value='1100')
        self.opacity=tk.StringVar(value='130')
        self.density=tk.StringVar(value='4')
        self.grid_on=tk.BooleanVar(value=True)
        self.logo=tk.StringVar()
        self.logo_scale=tk.StringVar(value='32')
        self.protection=tk.StringVar(value='adaptive')
        C={'base':'#0A101B','panel':'#141F30','raised':'#1B2B40','edge':'#2A3D55','text':'#ECF4FF','muted':'#92A9C3','accent':'#4AC7B1','bright':'#78E6D3'}
        self.palette=C
        style=ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background=C['panel'])
        style.configure('TLabel', background=C['panel'], foreground=C['text'], font=('Segoe UI',10))
        style.configure('TButton',font=('Segoe UI',10,'bold'),padding=(15,11),borderwidth=0,background=C['raised'],foreground=C['text'])
        style.map('TButton',background=[('active','#2B4A65'),('disabled','#263241')])
        style.configure('Accent.TButton',background=C['accent'],foreground='#082423',padding=(18,13),font=('Segoe UI',11,'bold'))
        style.map('Accent.TButton',background=[('active',C['bright']),('disabled','#496B69')])
        style.configure('TCheckbutton',background=C['panel'],foreground=C['text'],font=('Segoe UI',10))
        style.configure('TEntry',padding=9,fieldbackground='#EDF4FC',foreground='#132136')
        style.configure('TCombobox',padding=8)
        style.configure('TNotebook',background=C['base'],borderwidth=0)
        style.configure('TNotebook.Tab',font=('Segoe UI',10,'bold'),padding=(23,13),background=C['raised'],foreground=C['muted'])
        style.map('TNotebook.Tab',background=[('selected',C['accent'])],foreground=[('selected','#082423')])
        style.configure('Horizontal.TProgressbar',background=C['accent'],troughcolor=C['raised'],borderwidth=0)

        header=tk.Frame(self,bg=C['base'],padx=29,pady=19)
        header.pack(fill='x')
        logo=tk.Canvas(header,width=52,height=52,bg=C['base'],highlightthickness=0)
        logo.pack(side='left',padx=(0,13))
        logo.create_oval(5,5,47,47,outline=C['accent'],width=3)
        logo.create_line(15,27,24,36,39,17,fill=C['bright'],width=5,capstyle='round',joinstyle='round')
        brand=tk.Frame(header,bg=C['base']);brand.pack(side='left')
        tk.Label(brand,text='markveil',font=('Segoe UI',25,'bold'),fg=C['text'],bg=C['base']).pack(anchor='w')
        tk.Label(brand,text='IMAGE PROTECTION STUDIO  /  LOCAL-FIRST',font=('Segoe UI',9,'bold'),fg=C['muted'],bg=C['base']).pack(anchor='w')
        tk.Label(header,text='OPEN SOURCE   •   v0.9.0',font=('Segoe UI',10,'bold'),fg=C['accent'],bg=C['base']).pack(side='right')

        notebook=ttk.Notebook(self)
        notebook.pack(fill='both',expand=True,padx=25,pady=(0,10))
        protect=ttk.Frame(notebook,padding=22)
        labs=ttk.Frame(notebook,padding=22)
        about=ttk.Frame(notebook,padding=22)
        notebook.add(protect,text='  PROTEGER  ')
        notebook.add(labs,text='  LABORATÓRIO  ')
        notebook.add(about,text='  DESENVOLVEDORES  ')

        ttk.Label(protect,text='Proteja as suas prévias',font=('Segoe UI',21,'bold'),foreground=C['text']).pack(anchor='w',pady=(0,3))
        ttk.Label(protect,text='Marcas multicamada, originais preservados e processamento 100% local.',foreground=C['muted']).pack(anchor='w',pady=(0,16))
        self._folder(protect,'01   ORIGINAIS  ·  Pasta com fotografias',self.source)
        self._folder(protect,'02   DESTINO  ·  Onde salvar as prévias',self.target)
        columns=ttk.Frame(protect);columns.pack(fill='x',pady=(10,1))
        left=ttk.Frame(columns);left.pack(side='left',fill='both',expand=True,padx=(0,13))
        right=ttk.Frame(columns);right.pack(side='left',fill='both',expand=True,padx=(13,0))
        ttk.Label(left,text='03   IDENTIDADE DA MARCA',font=('Segoe UI',10,'bold'),foreground=C['accent']).pack(anchor='w',pady=(4,8))
        ttk.Label(left,text='Texto da marca d’água').pack(anchor='w',pady=(2,4))
        ttk.Entry(left,textvariable=self.mark).pack(fill='x')
        self._file(left,'Logotipo PNG (opcional)',self.logo)
        ttk.Label(left,text='Escala do logo (%)').pack(anchor='w',pady=(10,4))
        ttk.Entry(left,textvariable=self.logo_scale).pack(fill='x')
        ttk.Label(right,text='04   CONFIGURAÇÕES',font=('Segoe UI',10,'bold'),foreground=C['accent']).pack(anchor='w',pady=(4,8))
        ttk.Label(right,text='Perfil de proteção').pack(anchor='w',pady=(2,4))
        ttk.Combobox(right,textvariable=self.protection,values=['classic','adaptive','strong'],state='readonly').pack(fill='x')
        numbers=ttk.Frame(right);numbers.pack(fill='x',pady=(10,6))
        for idx,(label,var) in enumerate([('Tamanho (px)',self.size),('Opacidade',self.opacity),('Densidade',self.density)]):
            cell=ttk.Frame(numbers);cell.grid(row=0,column=idx,sticky='ew',padx=(0 if idx==0 else 4,4))
            numbers.columnconfigure(idx,weight=1)
            ttk.Label(cell,text=label).pack(anchor='w',pady=(0,4))
            ttk.Entry(cell,textvariable=var,width=9).pack(fill='x')
        ttk.Checkbutton(right,text='Grade de proteção adicional',variable=self.grid_on).pack(anchor='w',pady=(8,2))
        actions=ttk.Frame(protect);actions.pack(fill='x',pady=(18,8))
        ttk.Button(actions,text='VISUALIZAR',command=self.preview).pack(side='left',fill='x',expand=True,padx=(0,6))
        ttk.Button(actions,text='COMPARAR PERFIS',command=self.compare).pack(side='left',fill='x',expand=True,padx=(6,0))
        self.go=ttk.Button(protect,text='PROTEGER FOTOGRAFIAS  →',style='Accent.TButton',command=self.start)
        self.go.pack(fill='x',pady=(7,7))
        self.progress=ttk.Progressbar(protect,mode='indeterminate',style='Horizontal.TProgressbar')
        self.progress.pack(fill='x',pady=(2,0))
        ttk.Label(protect,text='As imagens originais não são sobrescritas. Nenhum arquivo é enviado para a nuvem.',foreground=C['muted'],font=('Segoe UI',9)).pack(anchor='w',pady=(7,0))

        ttk.Label(labs,text='Laboratório de resistência',font=('Segoe UI',21,'bold')).pack(anchor='w',pady=(0,5))
        ttk.Label(labs,text='Avalie suas prévias antes de publicá-las. Testes locais não garantem proteção contra toda IA.',foreground=C['muted']).pack(anchor='w',pady=(0,17))
        for title,desc,action in [
            ('Simulador de galerias','JPEG e redimensionamento típicos de publicação',self.gallery_lab),
            ('Teste de compressão','Relatório técnico de fidelidade das prévias',self.evaluate),
            ('Comparar com edição por IA','Importe o resultado obtido em uma ferramenta externa',self.external_attack),
            ('Proteção adversarial • experimental','Requer instalação opcional e um modelo VAE; não é garantia',self.adversarial_preview),
        ]:
            block=ttk.Frame(labs,padding=(13,11));block.pack(fill='x',pady=7)
            ttk.Label(block,text=title,font=('Segoe UI',12,'bold'),foreground=C['text']).pack(anchor='w')
            ttk.Label(block,text=desc,foreground=C['muted']).pack(anchor='w',pady=(3,9))
            ttk.Button(block,text='ABRIR FERRAMENTA  →',command=action).pack(anchor='w')

        ttk.Label(about,text='Feito para pessoas. Aberto para desenvolvedores.',font=('Segoe UI',19,'bold')).pack(anchor='w',pady=(0,12))
        for title,body in [
            ('CLI', 'markveil protect "C:\\Fotos" "C:\\Previas" --protection strong'),
            ('Servidor MCP', 'Instale: pip install -e ".[mcp]"  |  Inicie: markveil mcp'),
            ('Código aberto', 'Licença MIT. Contribuições, issues e documentação no repositório.'),
            ('Aviso científico', 'O projeto não garante bloquear remoção por IA. Teste com as ferramentas e condições reais do seu fluxo.'),
        ]:
            section=ttk.Frame(about,padding=13);section.pack(fill='x',pady=7)
            ttk.Label(section,text=title,foreground=C['accent'],font=('Segoe UI',12,'bold')).pack(anchor='w',pady=(0,4))
            ttk.Label(section,text=body,wraplength=750).pack(anchor='w')

        footer=tk.Frame(self,bg=C['base'],padx=25,pady=8);footer.pack(fill='x',side='bottom')
        tk.Label(footer,text='ATIVIDADE',font=('Segoe UI',9,'bold'),fg=C['muted'],bg=C['base']).pack(anchor='w')
        self.log=tk.Text(footer,height=3,bg='#101A28',fg='#C9E4F0',insertbackground='white',relief='flat',font=('Consolas',9),padx=11,pady=8)
        self.log.pack(fill='x',pady=(4,5))
        self.log.insert('end','Markveil pronto. Selecione suas fotos para começar.\n')
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
            dialog.title('Markveil · Visualização: '+photos[0].name)
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
            path=filedialog.asksaveasfilename(title='Salvar comparação',defaultextension='.jpg',filetypes=[('JPEG','*.jpg')],initialfile='markveil-comparacao.jpg')
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
        self.progress.start(10)
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
                    self.progress.stop()
                    if kind=='done': messagebox.showinfo('Concluído',msg)
                    else: messagebox.showerror('Erro',msg)
        except queue.Empty:
            pass
        self.after(120,self.poll)

def main():
    App().mainloop()

if __name__=='__main__': main()
