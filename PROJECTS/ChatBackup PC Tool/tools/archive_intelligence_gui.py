"""Optional R5 offline Tkinter window; deliberately separate from existing .pyw app."""
from __future__ import annotations
import json,sys,threading,tkinter as tk
from pathlib import Path
from tkinter import filedialog,messagebox,ttk,simpledialog
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from archive_intelligence import ArchiveCatalog,load_export,completeness
from archive_research import export_jsonl
from archive_extensions import import_directory, search_fts, conversation_view

BG='#090f1b';PANEL='#10192a';TXT='#edf4ff';CYAN='#00e8ff';PINK='#ff2acb'

class ArchiveWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('666 ChatBackup · Archive Intelligence R5 · OFFLINE')
        self.geometry('1030x700')
        self.configure(bg=BG)
        self.database=tk.StringVar(value=str(Path.home()/'.666chatbackup'/'catalog.sqlite3'))
        self.term=tk.StringVar()
        self.state=tk.StringVar(value='READY · Local-only; original exports remain unchanged')
        self.chats=[]
        self.cancel_requested=threading.Event()
        self.worker_active=False
        self.create_ui()

    def create_ui(self):
        root=tk.Frame(self,bg=BG,padx=20,pady=16);root.pack(fill='both',expand=True)
        tk.Label(root,text='666 CHATBACKUP · ARCHIVE INTELLIGENCE',fg=CYAN,bg=BG,font=('Segoe UI',17,'bold')).pack(anchor='w')
        tk.Label(root,text='OFFLINE IMPORT · SEARCH · COMPLETENESS · RAG JSONL',fg=PINK,bg=BG).pack(anchor='w',pady=(0,16))
        buttons=tk.Frame(root,bg=BG);buttons.pack(fill='x')
        tk.Button(buttons,text='Import official export ZIP',command=self.import_file).pack(side='left',padx=(0,8))
        tk.Button(buttons,text='Export RAG JSONL',command=self.export_rag).pack(side='left',padx=(0,8))
        tk.Button(buttons,text='Catalog status',command=self.info).pack(side='left')
        tk.Button(buttons,text='Batch import folder',command=self.batch_import).pack(side='left',padx=8)
        tk.Button(buttons,text='Cancel batch',command=self.cancel_batch).pack(side='left',padx=(0,8))
        tk.Button(buttons,text='View conversation',command=self.view_conversation).pack(side='left',padx=(0,8))
        index=tk.Frame(root,bg=BG);index.pack(fill='x',pady=12)
        tk.Label(index,text='SQLite catalog: ',bg=BG,fg=CYAN).pack(side='left')
        tk.Entry(index,textvariable=self.database).pack(side='left',fill='x',expand=True)
        tk.Button(index,text='Choose',command=self.choose_database).pack(side='left',padx=(8,0))
        search=tk.Frame(root,bg=BG);search.pack(fill='x',pady=(0,10))
        tk.Label(search,text='Search: ',bg=BG,fg=CYAN).pack(side='left')
        entry=tk.Entry(search,textvariable=self.term);entry.pack(side='left',fill='x',expand=True)
        entry.bind('<Return>',lambda event:self.search())
        tk.Button(search,text='Search',command=self.search).pack(side='left',padx=(8,0))
        tabs=ttk.Notebook(root);tabs.pack(fill='both',expand=True)
        self.matches=tk.Text(tabs,bg=PANEL,fg=TXT,wrap='word',insertbackground=TXT)
        self.report=tk.Text(tabs,bg=PANEL,fg=TXT,wrap='word',insertbackground=TXT)
        tabs.add(self.matches,text='Matches');tabs.add(self.report,text='Import and completeness')
        self.progress=ttk.Progressbar(root,orient='horizontal',mode='determinate',maximum=100)
        self.progress.pack(fill='x',pady=(8,0))
        tk.Label(root,textvariable=self.state,fg=CYAN,bg=BG,anchor='w').pack(fill='x',pady=(10,0))

    @staticmethod
    def show(widget,payload):
        widget.delete('1.0','end')
        widget.insert('end',json.dumps(payload,ensure_ascii=False,indent=2))

    def choose_database(self):
        chosen=filedialog.asksaveasfilename(defaultextension='.sqlite3',filetypes=[('SQLite','*.sqlite3')])
        if chosen:self.database.set(chosen)

    def run_worker(self,fn):
        if self.worker_active:
            self.state.set('BUSY · finish or cancel the current import first')
            return
        self.worker_active=True
        self.cancel_requested.clear()
        self.state.set('PROCESSING OFFLINE...')
        def run():
            try:
                fn()
            except Exception as exc:
                message=str(exc)
                self.after(0,lambda:self.error(message))
            finally:
                self.after(0,lambda:setattr(self,'worker_active',False))
        threading.Thread(target=run,daemon=True).start()

    def cancel_batch(self):
        if self.worker_active:
            self.cancel_requested.set()
            self.state.set('CANCELLATION REQUESTED · safe boundary; current JSON parse may finish')

    def update_progress(self,ev):
        self.progress['value']=ev.get('percent',0)
        stage=ev.get('stage','')
        name=ev.get('filename','')
        self.state.set(f"{stage} · {ev.get('completed_files',0)}/{ev.get('total_files',0)} · {name[:100]}")

    def error(self,message):
        self.state.set('ERROR · '+message[:140])
        messagebox.showerror('Archive Intelligence',message)

    def batch_import(self):
        folder=filedialog.askdirectory(title='Choose directory of official export ZIPs')
        if not folder:return
        db=self.database.get()
        checkpoint=db+'.batch-checkpoint.json'
        def work():
            result=import_directory(folder,db,checkpoint,stop=self.cancel_requested.is_set,
                     progress=lambda event:self.after(0,lambda value=event:self.update_progress(value)))
            def finish():
                self.show(self.report,result)
                self.state.set(f"BATCH {result['status']} · {result['imported']} files imported · {result['unchanged_files']} unchanged")
            self.after(0,finish)
        self.run_worker(work)

    def view_conversation(self):
        chat_id=simpledialog.askstring('Conversation viewer','Conversation ID from search results:',parent=self)
        if not chat_id:return
        try:
            with ArchiveCatalog(self.database.get()) as catalog:
                data=conversation_view(catalog,chat_id)
            if data is None:
                messagebox.showinfo('Conversation viewer','No indexed conversation with this ID')
                return
            win=tk.Toplevel(self)
            win.title('666 ChatBackup · '+data['title'][:90])
            win.geometry('940x660')
            pane=tk.Text(win,bg=PANEL,fg=TXT,wrap='word')
            pane.pack(fill='both',expand=True)
            pane.insert('end',f"{data['title']}\nSource: {data['source_file']}\nRevision: {data['revision']}\nIntegrity: {data['integrity']}\n\n")
            for message in data['messages']:
                pane.insert('end',f"[{message['role']}] {message['id']}\n{message['text']}\n\n")
            pane.configure(state='disabled')
        except Exception as exc:
            self.error(str(exc))

    def import_file(self):
        path=filedialog.askopenfilename(filetypes=[('ZIP export','*.zip')])
        if not path:return
        db=self.database.get()
        def work():
            chats,inspection=load_export(path)
            with ArchiveCatalog(db) as catalog:
                updated=catalog.add(chats,inspection['sha256'],Path(path).name)
                counts=catalog.status()
            report={'source':inspection,'indexed':updated,'catalog':counts,
                    'completeness':[completeness(c) for c in chats]}
            def finish():
                self.chats=chats
                self.show(self.report,report)
                self.state.set(f"IMPORT {inspection['status']} · {len(chats)} conversations")
            self.after(0,finish)
        self.run_worker(work)

    def search(self):
        term=self.term.get().strip()
        if not term:return
        db=self.database.get()
        def work():
            with ArchiveCatalog(db) as catalog:rows=search_fts(catalog,term,limit=200)
            self.after(0,lambda:self.show(self.matches,rows))
            self.after(0,lambda:self.state.set(f'{len(rows)} local results'))
        self.run_worker(work)

    def info(self):
        with ArchiveCatalog(self.database.get()) as catalog:status=catalog.status()
        messagebox.showinfo('Local catalog',json.dumps(status,indent=2))

    def export_rag(self):
        if not self.chats:
            messagebox.showinfo('RAG','Import a data-export ZIP first.');return
        output=filedialog.asksaveasfilename(defaultextension='.jsonl',filetypes=[('JSONL','*.jsonl')])
        if not output:return
        try:messagebox.showinfo('Export',json.dumps(export_jsonl(self.chats,output),indent=2))
        except Exception as exc:self.error(str(exc))

if __name__=='__main__':
    ArchiveWindow().mainloop()
