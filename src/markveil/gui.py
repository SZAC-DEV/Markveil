"""Desktop UI; processing runs in worker thread so GUI remains responsive."""
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import tempfile
import sys
from .settings import save_preset, load_preset, list_presets
from .resources import sample_resources
from .comparison import compare_profiles
from .benchmark import benchmark_photo
from .gallery_lab import gallery_test
from .attack_lab import attack_test
from .core import create_preview
from .core import Options, process_directory

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Markveil Studio · Proteção de fotografias')
        self._set_app_icon()
        self.geometry('1270x840')
        self.minsize(1080, 710)
        self.configure(bg='#0A101B')
        self.q = queue.Queue()
        self.source = tk.StringVar()
        self.target = tk.StringVar()
        self.mark = tk.StringVar(value='PREVIEW • NOT PURCHASED')
        self.size = tk.StringVar(value='1100')
        self.opacity = tk.StringVar(value='130')
        self.density = tk.StringVar(value='4')
        self.grid_on = tk.BooleanVar(value=True)
        self.logo = tk.StringVar()
        self.logo_scale = tk.StringVar(value='32')
        self.protection = tk.StringVar(value='adaptive')
        self.selected_photo = tk.StringVar()
        self.preview_image = None
        self.comparison_fraction = tk.DoubleVar(value=50)
        self.compare_mode = tk.BooleanVar(value=True)
        self.original_preview_path = None
        self.protected_preview_path = None
        self.preview_path = None
        self.files = []
        self.finished = 0
        self.busy = False
        C = {'base':'#0A101B','panel':'#141F30','raised':'#1B2B40','edge':'#2A3D55',
             'text':'#ECF4FF','muted':'#92A9C3','accent':'#4AC7B1','bright':'#78E6D3'}
        self.palette = C
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame',background=C['panel'])
        style.configure('TLabel',background=C['panel'],foreground=C['text'],font=('Segoe UI',10))
        style.configure('TButton',background=C['raised'],foreground=C['text'],font=('Segoe UI',10,'bold'),padding=(12,9),borderwidth=0)
        style.map('TButton',background=[('active','#30506A')])
        style.configure('Accent.TButton',background=C['accent'],foreground='#082423',font=('Segoe UI',11,'bold'),padding=(16,12))
        style.map('Accent.TButton',background=[('active',C['bright'])])
        style.configure('TEntry',padding=7,fieldbackground='#E9F2F8',foreground='#112136')
        style.configure('TCombobox',padding=7)
        style.configure('TCheckbutton',background=C['panel'],foreground=C['text'])
        style.configure('TNotebook',background=C['base'],borderwidth=0)
        style.configure('TNotebook.Tab',background=C['raised'],foreground=C['muted'],padding=(22,12),font=('Segoe UI',10,'bold'))
        style.map('TNotebook.Tab',background=[('selected',C['accent'])],foreground=[('selected','#082423')])
        style.configure('Horizontal.TProgressbar',background=C['accent'],troughcolor=C['raised'],borderwidth=0)
        header=tk.Frame(self,bg=C['base'],padx=26,pady=18)
        header.pack(fill='x')
        emblem=tk.Canvas(header,width=49,height=49,bg=C['base'],highlightthickness=0)
        emblem.pack(side='left',padx=(0,12))
        emblem.create_oval(4,4,45,45,outline=C['accent'],width=2)
        emblem.create_line(14,25,23,34,36,16,fill=C['accent'],width=4,capstyle='round',joinstyle='round')
        brand=tk.Frame(header,bg=C['base']);brand.pack(side='left')
        tk.Label(brand,text='markveil',font=('Segoe UI',24,'bold'),bg=C['base'],fg=C['text']).pack(anchor='w')
        tk.Label(brand,text='PHOTO PROTECTION STUDIO  /  LOCAL FIRST',font=('Segoe UI',9),bg=C['base'],fg=C['muted']).pack(anchor='w')
        tk.Label(header,text='OPEN SOURCE   ·   v0.11.0',font=('Segoe UI',10,'bold'),bg=C['base'],fg=C['accent']).pack(side='right')
        tabs=ttk.Notebook(self)
        tabs.pack(fill='both',expand=True,padx=22,pady=(0,8))
        protect=ttk.Frame(tabs,padding=15)
        labs=ttk.Frame(tabs,padding=18)
        about=ttk.Frame(tabs,padding=18)
        tabs.add(protect,text='  ESTÚDIO  ')
        tabs.add(labs,text='  LABORATÓRIO  ')
        tabs.add(about,text='  DESENVOLVEDORES  ')
        work=ttk.Frame(protect)
        work.pack(fill='both',expand=True)
        left=ttk.Frame(work)
        left.pack(side='left',fill='both',expand=False,padx=(0,17))
        left.configure(width=440)
        left.pack_propagate(False)
        right=ttk.Frame(work)
        right.pack(side='left',fill='both',expand=True)
        ttk.Label(left,text='Crie prévias protegidas',font=('Segoe UI',17,'bold')).pack(anchor='w',pady=(0,4))
        ttk.Label(left,text='Original intacto. Exportação local.',foreground=C['muted']).pack(anchor='w',pady=(0,12))
        self._folder(left,'FOTOGRAFIAS  /  Pasta de origem',self.source)
        self._drop_area(left)
        ttk.Button(left,text='CARREGAR FOTOGRAFIAS  ↗',command=self.load_files).pack(fill='x',pady=(9,6))
        self._folder(left,'EXPORTAÇÃO  /  Pasta de destino',self.target)
        ttk.Label(left,text='MARCA D’ÁGUA',font=('Segoe UI',10,'bold'),foreground=C['accent']).pack(anchor='w',pady=(13,5))
        ttk.Entry(left,textvariable=self.mark).pack(fill='x')
        self._file(left,'Logo personalizado (PNG)',self.logo)
        ttk.Label(left,text='PERFIL DE PROTEÇÃO',font=('Segoe UI',10,'bold'),foreground=C['accent']).pack(anchor='w',pady=(13,5))
        ttk.Combobox(left,textvariable=self.protection,values=['classic','adaptive','strong'],state='readonly').pack(fill='x')
        parameters=ttk.Frame(left);parameters.pack(fill='x',pady=(12,4))
        for idx,(label,var) in enumerate([('Tamanho px',self.size),('Opacidade',self.opacity),('Densidade',self.density),('Logo %',self.logo_scale)]):
            block=ttk.Frame(parameters)
            block.grid(row=0,column=idx,sticky='ew',padx=(0,6))
            parameters.columnconfigure(idx,weight=1)
            ttk.Label(block,text=label,font=('Segoe UI',9)).pack(anchor='w',pady=(0,4))
            ttk.Entry(block,textvariable=var,width=7).pack(fill='x')
        ttk.Checkbutton(left,text='Grade de proteção adicional',variable=self.grid_on).pack(anchor='w',pady=(8,9))
        self._preset_controls(left)
        ttk.Button(left,text='ATUALIZAR PRÉVIA',command=self.preview).pack(fill='x',pady=(4,5))
        self.go=ttk.Button(left,text='PROTEGER TODAS AS FOTOS  →',style='Accent.TButton',command=self.start)
        self.go.pack(fill='x',pady=(7,6))
        self.progress=ttk.Progressbar(left,mode='determinate',maximum=100)
        self.progress.pack(fill='x',pady=(5,4))
        self.status=ttk.Label(left,text='Pronto para começar',foreground=C['muted'])
        self.status.pack(anchor='w')
        ttk.Label(right,text='Prévia em tempo real',font=('Segoe UI',17,'bold')).pack(anchor='w',pady=(0,5))
        ttk.Label(right,text='Selecione uma fotografia na lista para comparar original e prévia.',foreground=C['muted']).pack(anchor='w',pady=(0,10))
        photos_frame=ttk.Frame(right)
        photos_frame.pack(fill='x',pady=(0,10))
        self.file_list=tk.Listbox(photos_frame,height=5,bg='#1B2B40',fg=C['text'],selectbackground='#2C665D',selectforeground='white',relief='flat',borderwidth=0,activestyle='none',font=('Segoe UI',10),highlightthickness=0)
        self.file_list.pack(side='left',fill='x',expand=True)
        scroll=ttk.Scrollbar(photos_frame,orient='vertical',command=self.file_list.yview)
        scroll.pack(side='right',fill='y')
        self.file_list.config(yscrollcommand=scroll.set)
        self.file_list.bind('<<ListboxSelect>>',self._on_file_selected)
        self.image_canvas=tk.Canvas(right,bg='#101A28',highlightthickness=0,height=280)
        self.image_canvas.pack(fill='both',expand=True)
        self.image_canvas.bind('<Configure>',self._redraw_preview)
        self.image_canvas.bind('<Button-1>',self._drag_comparison)
        self.image_canvas.bind('<B1-Motion>',self._drag_comparison)
        self.preview_note=ttk.Label(right,text='Selecione uma pasta e carregue as fotos.',foreground=C['muted'])
        self.preview_note.pack(anchor='w',pady=(8,4))
        slider_row=ttk.Frame(right);slider_row.pack(fill='x',pady=(5,3))
        ttk.Checkbutton(slider_row,text='Comparar antes/depois',variable=self.compare_mode,command=self._redraw_preview).pack(side='left')
        ttk.Scale(slider_row,from_=0,to=100,variable=self.comparison_fraction,command=lambda _value:self._redraw_preview()).pack(side='left',fill='x',expand=True,padx=(12,0))
        self.resource_label=ttk.Label(right,text='CPU: —  ·  RAM: —  ·  GPU: não detectada',foreground=C['muted'])
        self.resource_label.pack(anchor='w',pady=(10,0))
        ttk.Label(labs,text='Laboratório de resistência',font=('Segoe UI',21,'bold')).pack(anchor='w',pady=(0,10))
        ttk.Label(labs,text='Testes locais exploratórios. Nenhuma técnica garante impedir remoção por IA.',foreground=C['muted']).pack(anchor='w',pady=(0,16))
        for title,desc,action in [
            ('Simulação de galerias','Compressão JPEG e redimensionamento',self.gallery_lab),
            ('Benchmark de compressão','Relatório de diferenças e fidelidade',self.evaluate),
            ('Remoção com IA externa','Importar uma imagem editada para comparação',self.external_attack),
            ('Proteção adversarial experimental','Necessita modelo VAE e dependências opcionais',self.adversarial_preview),
            ('Comparar perfis','Exportar painel de comparação com 3 perfis',self.compare),
        ]:
            box=ttk.Frame(labs,padding=12)
            box.pack(fill='x',pady=5)
            ttk.Label(box,text=title,font=('Segoe UI',12,'bold')).pack(anchor='w')
            ttk.Label(box,text=desc,foreground=C['muted']).pack(anchor='w',pady=(2,6))
            ttk.Button(box,text='EXECUTAR  →',command=action).pack(anchor='w')
        ttk.Label(about,text='Ferramentas para desenvolvedores',font=('Segoe UI',21,'bold')).pack(anchor='w',pady=(0,18))
        for heading,command in [('Interface','markveil gui'),('CLI','markveil protect "C:\\Fotos" "C:\\Previas" --protection strong'),('MCP','pip install -e ".[mcp]"  &&  markveil mcp')]:
            ttk.Label(about,text=heading,foreground=C['accent'],font=('Segoe UI',12,'bold')).pack(anchor='w',pady=(12,4))
            ttk.Label(about,text=command,font=('Consolas',11)).pack(anchor='w')
        ttk.Label(about,text='MIT · Código aberto · Nenhuma API paga · Resultados experimentais não representam garantia de proteção',wraplength=780,foreground=C['muted']).pack(anchor='w',pady=(24,0))
        footer=tk.Frame(self,bg=C['base'],padx=22,pady=8)
        footer.pack(fill='x')
        self.log=tk.Text(footer,height=2,bg='#101A28',fg='#D1E5F3',insertbackground='white',relief='flat',font=('Consolas',9),padx=9,pady=7)
        self.log.pack(fill='x')
        self.log.insert('end','Markveil pronto. As fotografias originais nunca são modificadas.\n')
        self.after(60,self._maximize_at_start)
        self.after(100,self.poll)
        self.after(1000,self._update_resources)
        self.after(100,self._enable_drop)

    def load_files(self):
        from .core import SUPPORTED
        folder=Path(self.source.get())
        if not folder.is_dir():
            messagebox.showerror('Pasta inválida','Escolha uma pasta existente com fotografias.')
            return
        self.files=sorted((p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED),key=str)
        self.file_list.delete(0,'end')
        for file in self.files:
            self.file_list.insert('end',str(file.relative_to(folder)))
        self.status.configure(text=f'{len(self.files)} fotografias encontradas')
        if self.files:
            self.file_list.selection_set(0)
            self._on_file_selected()
        else:
            self.preview_path=None
            self.original_preview_path=None
            self.protected_preview_path=None
            self._redraw_preview()

    def _on_file_selected(self,event=None):
        indexes=self.file_list.curselection()
        if indexes and indexes[0]<len(self.files):
            self.preview_path=self.files[indexes[0]]
            self.original_preview_path=self.preview_path
            self.protected_preview_path=None
            self.preview_note.configure(text=self.preview_path.name+'  ·  Original (sem prévia de proteção)')
            self._redraw_preview()

    def _redraw_preview(self,event=None):
        canvas=self.image_canvas
        canvas.delete('all')
        w=max(canvas.winfo_width(),200)
        h=max(canvas.winfo_height(),180)
        original=self.original_preview_path or self.preview_path
        if not original:
            canvas.create_text(w//2,h//2,text='Suas fotografias aparecerão aqui',fill='#92A9C3',font=('Segoe UI',14))
            return
        try:
            with Image.open(original) as image:
                base=image.convert('RGB')
            base.thumbnail((max(w-30,100),max(h-30,100)),Image.Resampling.LANCZOS)
            protected=self.protected_preview_path
            if protected and self.compare_mode.get():
                with Image.open(protected) as image:
                    after=image.convert('RGB').resize(base.size,Image.Resampling.LANCZOS)
                cut=round(base.width*self.comparison_fraction.get()/100)
                base.paste(after.crop((cut,0,base.width,base.height)),(cut,0))
                x0=(w-base.width)//2
                canvas.create_line(x0+cut,(h-base.height)//2,x0+cut,(h+base.height)//2,fill='#4AC7B1',width=3)
            elif protected:
                with Image.open(protected) as image:
                    base=image.convert('RGB')
                base.thumbnail((max(w-30,100),max(h-30,100)),Image.Resampling.LANCZOS)
            self.preview_image=ImageTk.PhotoImage(base,master=self)
            canvas.create_image(w//2,h//2,image=self.preview_image)
            if protected and self.compare_mode.get():
                x0=(w-base.width)//2
                cut=round(base.width*self.comparison_fraction.get()/100)
                canvas.create_line(x0+cut,(h-base.height)//2,x0+cut,(h+base.height)//2,fill='#4AC7B1',width=3)
                canvas.create_text(12,12,anchor='nw',text='ORIGINAL  |  PROTEGIDA',fill='#4AC7B1',font=('Segoe UI',10,'bold'))
        except (OSError,ValueError) as exc:
            canvas.create_text(w//2,h//2,text=f'Não foi possível carregar: {exc}',fill='#FFB4B4')

    def _drag_comparison(self,event):
        if self.protected_preview_path and self.compare_mode.get():
            width=max(self.image_canvas.winfo_width(),1)
            self.comparison_fraction.set(max(0,min(100,100*event.x/width)))
            self._redraw_preview()

    def _maximize_at_start(self):
        self.geometry('1350x850')
        self.minsize(1060,700)
        try:
            if sys.platform.startswith('win'):
                self.state('zoomed')
            else:
                self.attributes('-zoomed',True)
        except tk.TclError:
            pass

    def _set_app_icon(self):
        assets=Path(__file__).resolve().parent/'assets'
        try:
            if sys.platform.startswith('win') and (assets/'markveil.ico').exists():
                self.iconbitmap(str(assets/'markveil.ico'))
            elif (assets/'markveil.png').exists():
                self._icon_photo=tk.PhotoImage(file=str(assets/'markveil.png'))
                self.iconphoto(True,self._icon_photo)
        except tk.TclError:
            pass

    def _preset_controls(self,parent):
        row=ttk.Frame(parent);row.pack(fill='x',pady=(5,7))
        self.preset_name=tk.StringVar(value='Meu preset')
        ttk.Entry(row,textvariable=self.preset_name,width=17).pack(side='left',fill='x',expand=True)
        ttk.Button(row,text='Salvar preset',command=self._save_preset).pack(side='left',padx=(5,0))
        ttk.Button(row,text='Carregar',command=self._load_preset).pack(side='left',padx=(5,0))

    def _save_preset(self):
        try:
            opts=self._build_processing_options()
            save_preset(self.preset_name.get(),opts)
            self.status.configure(text='Preset salvo no computador')
        except (ValueError,OSError) as exc:
            messagebox.showerror('Preset inválido',str(exc))

    def _load_preset(self):
        try:
            from tkinter import simpledialog
            names=list_presets()
            if not names:
                raise ValueError('Nenhum preset salvo ainda.')
            name=simpledialog.askstring('Carregar preset','Presets: '+', '.join(names)+'\nDigite o nome:',initialvalue=names[0],parent=self)
            if not name:return
            opts=load_preset(name)
            for field,value in [('mark',opts.text),('size',opts.max_size),('opacity',opts.opacity),('density',opts.density),('logo',opts.logo_path),('logo_scale',opts.logo_scale),('protection',opts.protection)]:
                getattr(self,field).set(str(value))
            self.grid_on.set(opts.grid)
            self.preset_name.set(name)
        except (ValueError,OSError) as exc:
            messagebox.showerror('Preset indisponível',str(exc))

    def _drop_area(self,parent):
        self.drop_box=tk.Label(parent,text='⇩  Arraste fotos ou pastas aqui (quando disponível)',bg='#1B2B40',fg='#A9CBD4',font=('Segoe UI',9),pady=11)
        self.drop_box.pack(fill='x',pady=(7,0))

    def _enable_drop(self):
        try:
            from tkinterdnd2 import TkinterDnD, DND_FILES
            # TkinterDnD initializes the tkdnd extension on an existing Tk root.
            TkinterDnD._require(self)
            self.drop_box.drop_target_register(DND_FILES)
            self.drop_box.dnd_bind('<<Drop>>',self._on_drop)
            self.drop_box.configure(text='⇩  Arraste fotografias ou uma pasta aqui')
        except (ImportError,tk.TclError,RuntimeError):
            self.drop_box.configure(text='Arrastar e soltar opcional: instale tkinterdnd2')

    def _on_drop(self,event):
        paths=[Path(p) for p in self.tk.splitlist(event.data)]
        from .core import SUPPORTED
        photos=[]
        for path in paths:
            if path.is_dir():
                photos.extend(p for p in path.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED)
            elif path.is_file() and path.suffix.lower() in SUPPORTED:
                photos.append(path)
        photos=sorted(set(photos),key=str)
        if not photos:return
        self.files=photos
        self.source.set(str(photos[0].parent))
        self.file_list.delete(0,'end')
        for photo in photos:self.file_list.insert('end',photo.name)
        self.file_list.selection_set(0)
        self._on_file_selected()
        self.status.configure(text=f'{len(photos)} fotos arrastadas')

    def _update_resources(self):
        try:
            data=sample_resources()
            self.resource_label.configure(text=data['label'])
        except Exception:
            self.resource_label.configure(text='Monitor de recursos indisponível')
        self.after(2000,self._update_resources)

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
            if not self.files:
                self.load_files()
            if not self.files:
                raise ValueError('Selecione uma pasta com fotografias.')
            selected=self.file_list.curselection()
            source=self.files[selected[0]] if selected else self.files[0]
            if not hasattr(self,'_preview_temp'):
                self._preview_temp=tempfile.TemporaryDirectory(prefix='markveil-ui-')
            dest=Path(self._preview_temp.name)/'previa.jpg'
            create_preview(source,dest,options)
            self.original_preview_path=source
            self.protected_preview_path=dest
            self.preview_path=source
            self.preview_note.configure(text=f'Prévia protegida de {source.name}  ·  {options.protection}')
            self._redraw_preview()
        except (ValueError,OSError,TypeError) as exc:
            messagebox.showerror('Prévia indisponível',str(exc))

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
        self.busy=True
        self.finished=0
        self.progress.configure(value=0)
        self.status.configure(text='Processando fotografias...')
        self.log.delete('1.0','end')
        def work():
            try:
                result=process_directory(inp,out,options,lambda line:self.q.put(('line',line)))
                self.q.put(('done',f"{len(result['images'])} prévias geradas, {len(result['errors'])} erros.\nRelatório em {out}"))
            except Exception as exc:
                self.q.put(('error',str(exc)))
        threading.Thread(target=work,daemon=True).start()

    def _count_sources(self):
        from .core import SUPPORTED
        folder=Path(self.source.get())
        return sum(1 for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED) if folder.is_dir() else 0

    def poll(self):
        try:
            while True:
                kind,msg=self.q.get_nowait()
                if kind=='line':
                    self.finished+=1
                    count=len(self.files) if self.files else self._count_sources()
                    self.progress.configure(value=100*self.finished/max(1,count))
                    self.status.configure(text=f'{self.finished}/{count} fotografias processadas')
                    self.log.insert('end',msg+'\n')
                    self.log.see('end')
                else:
                    self.go.configure(state='normal')
                    self.busy=False
                    self.status.configure(text='Concluído' if kind=='done' else 'Ocorreu um erro')
                    if kind=='done': messagebox.showinfo('Concluído',msg)
                    else: messagebox.showerror('Erro',msg)
        except queue.Empty:
            pass
        self.after(120,self.poll)

def main():
    App().mainloop()

if __name__=='__main__': main()
