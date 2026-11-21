"""Optional R5 offline Tkinter window; deliberately separate from existing .pyw app."""
from __future__ import annotations
import json,sys,threading,tkinter as tk
from pathlib import Path
from tkinter import filedialog,messagebox,ttk,simpledialog
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from archive_intelligence import ArchiveCatalog,load_export,completeness
from archive_research import export_jsonl
from archive_extensions import import_directory, search_fts, conversation_view
from archive_navigation import browse_conversations, search_filtered, audit_sources
from archive_source_relocation import propose_relocations
from archive_message_navigation import message_position, message_context, branch_index, branch_context

BG='#090f1b';PANEL='#10192a';TXT='#edf4ff';CYAN='#00e8ff';PINK='#ff2acb'

class ArchiveWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('666 ChatBackup · Archive Intelligence R5 · OFFLINE')
        self.geometry('1030x700')
        self.configure(bg=BG)
        self.database=tk.StringVar(value=str(Path.home()/'.666chatbackup'/'catalog.sqlite3'))
        self.term=tk.StringVar()
        self.source_filter=tk.StringVar()
        self.role_filter=tk.StringVar(value='Any role')
        self.search_rows=[]
        self.last_search_term=''
        self.archive_rows=[]
        self.relocation_rows=[]
        self.archive_offset=0
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
        tk.Button(buttons,text='Check source ZIPs',command=self.audit_source_folder).pack(side='left',padx=(0,8))
        tk.Button(buttons,text='Find moved ZIPs',command=self.find_moved_sources).pack(side='left',padx=(0,8))
        index=tk.Frame(root,bg=BG);index.pack(fill='x',pady=12)
        tk.Label(index,text='SQLite catalog: ',bg=BG,fg=CYAN).pack(side='left')
        tk.Entry(index,textvariable=self.database).pack(side='left',fill='x',expand=True)
        tk.Button(index,text='Choose',command=self.choose_database).pack(side='left',padx=(8,0))
        search=tk.Frame(root,bg=BG);search.pack(fill='x',pady=(0,10))
        tk.Label(search,text='Search: ',bg=BG,fg=CYAN).pack(side='left')
        entry=tk.Entry(search,textvariable=self.term);entry.pack(side='left',fill='x',expand=True)
        entry.bind('<Return>',lambda event:self.search())
        tk.Button(search,text='Search',command=self.search).pack(side='left',padx=(8,0))
        options=tk.Frame(root,bg=BG);options.pack(fill='x',pady=(0,8))
        tk.Label(options,text='Source: ',bg=BG,fg=CYAN).pack(side='left')
        tk.Entry(options,textvariable=self.source_filter,width=28).pack(side='left',padx=(0,12))
        tk.Label(options,text='Role: ',bg=BG,fg=CYAN).pack(side='left')
        ttk.Combobox(options,textvariable=self.role_filter,width=16,state='readonly',
                     values=('Any role','user','assistant','system','tool','developer')).pack(side='left')
        tk.Button(options,text='Browse conversations',command=self.browse).pack(side='left',padx=(10,0))
        tk.Button(options,text='Next page',command=self.next_page).pack(side='left',padx=(8,0))
        tabs=ttk.Notebook(root);tabs.pack(fill='both',expand=True)
        self.tabs=tabs
        self.matches=tk.Text(tabs,bg=PANEL,fg=TXT,wrap='word',insertbackground=TXT)
        self.report=tk.Text(tabs,bg=PANEL,fg=TXT,wrap='word',insertbackground=TXT)
        tabs.add(self.matches,text='Matches');tabs.add(self.report,text='Import and completeness')
        hits_tab=tk.Frame(tabs,bg=PANEL)
        tk.Label(hits_tab,text='DOUBLE-CLICK A SEARCH RESULT TO OPEN EXACT MESSAGE',
                 fg=CYAN,bg=PANEL).pack(anchor='w',padx=8,pady=6)
        self.search_list=ttk.Treeview(
            hits_tab,columns=('title','role','source','snippet'),
            show='headings',selectmode='browse')
        for key,label,width in (('title','Conversation',260),('role','Role',85),
                                ('source','Source',160),('snippet','Match preview',420)):
            self.search_list.heading(key,text=label)
            self.search_list.column(key,width=width,minwidth=65)
        self.search_list.pack(fill='both',expand=True,padx=8,pady=4)
        self.search_list.bind('<Double-1>',lambda event:self.open_selected_hit())
        tk.Button(hits_tab,text='Open selected message',
                  command=self.open_selected_hit).pack(anchor='e',padx=8,pady=6)
        tabs.add(hits_tab,text='Search navigation')
        self.hits_tab=hits_tab
        browse_tab=tk.Frame(tabs,bg=PANEL)
        self.archive_list=ttk.Treeview(browse_tab,columns=('title','source','count','integrity'),
                                      show='headings',selectmode='browse')
        for key,label,width in (('title','Conversation',360),('source','Source',190),
                                ('count','Messages',80),('integrity','Integrity',210)):
            self.archive_list.heading(key,text=label)
            self.archive_list.column(key,width=width,minwidth=60)
        self.archive_list.pack(fill='both',expand=True)
        self.archive_list.bind('<Double-1>',lambda event:self.open_selected_archive())
        tk.Button(browse_tab,text='Open selected conversation',
                  command=self.open_selected_archive).pack(anchor='e',pady=6)
        tabs.add(browse_tab,text='Archive navigation')
        relocation_tab=tk.Frame(tabs,bg=PANEL)
        tk.Label(relocation_tab,text='SHA-256 SOURCE RELOCATION · READ-ONLY SUGGESTIONS',
                 fg=CYAN,bg=PANEL,anchor='w').pack(fill='x',padx=8,pady=(8,4))
        self.relocation_list=ttk.Treeview(
            relocation_tab,columns=('status','original','candidates'),show='headings',selectmode='browse')
        for key,label,width in (('status','Status',170),('original','Original ZIP',340),
                                ('candidates','Verified-hash candidate(s)',430)):
            self.relocation_list.heading(key,text=label)
            self.relocation_list.column(key,width=width,minwidth=90)
        self.relocation_list.pack(fill='both',expand=True,padx=8,pady=4)
        tk.Button(relocation_tab,text='Scan selected source folder (no changes)',
                  command=self.find_moved_sources).pack(anchor='e',padx=8,pady=6)
        tabs.add(relocation_tab,text='Source relocation')
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

    def browse(self,reset=True):
        if reset:self.archive_offset=0
        db=self.database.get()
        source=self.source_filter.get().strip()
        term=self.term.get().strip()
        offset=self.archive_offset
        def work():
            with ArchiveCatalog(db) as catalog:
                rows=browse_conversations(catalog,title=term,source=source,
                                          limit=100,offset=offset)
            def finish():
                self.archive_rows=rows
                for child in self.archive_list.get_children():self.archive_list.delete(child)
                for idx,row in enumerate(rows):
                    self.archive_list.insert('', 'end', iid=str(idx),
                        values=(row['title'],row['source'],row['messages'],row['integrity']))
                self.state.set(f'ARCHIVE PAGE {offset//100+1} · {len(rows)} conversations')
            self.after(0,finish)
        self.run_worker(work)

    def next_page(self):
        self.archive_offset+=100
        self.browse(reset=False)

    def open_selected_archive(self):
        selected=self.archive_list.selection()
        if not selected:return
        idx=int(selected[0])
        if idx>=len(self.archive_rows):return
        self.view_conversation(self.archive_rows[idx]['conversation_id'])

    def audit_source_folder(self):
        folder=filedialog.askdirectory(title='Folder containing previously imported ZIPs')
        if not folder:return
        db=self.database.get()
        checkpoint=db+'.batch-checkpoint.json'
        def work():
            result=audit_sources(folder,checkpoint)
            def finish():
                self.show(self.report,result)
                self.state.set(f"SOURCE AUDIT {result['status']} · {result['checked']} ZIPs")
            self.after(0,finish)
        self.run_worker(work)

    def find_moved_sources(self):
        """Display hash-verified suggestions without moving or rewriting any source."""
        folder=filedialog.askdirectory(title='Locate current folder of ChatGPT export ZIPs')
        if not folder:return
        checkpoint=self.database.get()+'.batch-checkpoint.json'
        if not Path(checkpoint).is_file():
            checkpoint=filedialog.askopenfilename(
                title='Select existing batch checkpoint (read-only)',filetypes=[('JSON','*.json')])
            if not checkpoint:return
        def work():
            report=propose_relocations(folder,checkpoint)
            def finish():
                self.relocation_rows=report['sources']
                for child in self.relocation_list.get_children():
                    self.relocation_list.delete(child)
                for idx,row in enumerate(self.relocation_rows):
                    self.relocation_list.insert('','end',iid=str(idx),
                        values=(row['status'],row['source'],', '.join(row['candidates'])))
                self.show(self.report,report)
                found=sum(row['status']=='RELOCATED_CANDIDATE' for row in self.relocation_rows)
                ambiguous=sum(row['status']=='AMBIGUOUS' for row in self.relocation_rows)
                self.state.set(f"SOURCE RELOCATION · {found} candidate(s), {ambiguous} ambiguous · NO FILES CHANGED")
            self.after(0,finish)
        self.run_worker(work)

    def open_selected_hit(self):
        selected=self.search_list.selection()
        if not selected:return
        idx=int(selected[0])
        if idx<0 or idx>=len(self.search_rows):return
        hit=self.search_rows[idx]
        self.view_conversation(hit['conversation_id'],hit['message_id'],self.last_search_term)

    def view_conversation(self,chat_id=None,message_id=None,highlight=''):
        if chat_id is None:
            chat_id=simpledialog.askstring('Conversation viewer','Conversation ID from search results:',parent=self)
        if not chat_id:return
        try:
            with ArchiveCatalog(self.database.get()) as catalog:
                data=conversation_view(catalog,chat_id)
            if data is None:
                messagebox.showinfo('Conversation viewer','No indexed conversation with this ID')
                return
            index=message_position(data,message_id)
            graph=branch_index(data)
            if index<0:
                messagebox.showinfo('Conversation viewer','No indexed messages in this conversation')
                return
            win=tk.Toplevel(self)
            win.title('666 ChatBackup · '+data['title'][:90])
            win.geometry('940x660')
            header=tk.Frame(win,bg=BG);header.pack(fill='x')
            location=tk.StringVar()
            tk.Label(header,textvariable=location,bg=BG,fg=CYAN,anchor='w').pack(
                side='left',fill='x',expand=True,padx=12,pady=8)
            branchbar=tk.Frame(win,bg=BG);branchbar.pack(fill='x',padx=8)
            branch_status=tk.StringVar()
            tk.Label(branchbar,textvariable=branch_status,bg=BG,fg=PINK,anchor='w').pack(
                fill='x',pady=(2,5))
            parent_button=tk.Button(branchbar,text='Parent',width=10)
            parent_button.pack(side='left',padx=(0,5))
            child_choice=ttk.Combobox(branchbar,state='readonly',width=29)
            child_choice.pack(side='left',padx=5)
            child_button=tk.Button(branchbar,text='Go to child',width=12)
            child_button.pack(side='left',padx=5)
            sibling_choice=ttk.Combobox(branchbar,state='readonly',width=29)
            sibling_choice.pack(side='left',padx=5)
            sibling_button=tk.Button(branchbar,text='Switch branch',width=14)
            sibling_button.pack(side='left',padx=5)
            pane=tk.Text(win,bg=PANEL,fg=TXT,wrap='word',insertbackground=TXT)
            pane.pack(fill='both',expand=True)
            pane.tag_configure('selected',background='#253750',foreground=TXT)
            pane.tag_configure('highlight',background='#ffcc33',foreground='#101015')
            def render():
                result=message_context(data,index,radius=2,highlight=highlight)
                relation=branch_context(data,index,graph=graph)
                child_positions=relation['children']
                sibling_positions=relation['siblings']
                parent_pos=relation['parent']
                parent_button.configure(state='normal' if parent_pos is not None else 'disabled')
                child_choice['values']=[f"{pos+1}/{len(data['messages'])} · {data['messages'][pos]['id']}" for pos in child_positions]
                sibling_choice['values']=[f"{pos+1}/{len(data['messages'])} · {data['messages'][pos]['id']}" for pos in sibling_positions]
                child_choice.current(0) if child_positions else child_choice.set('')
                sibling_choice.current(0) if sibling_positions else sibling_choice.set('')
                child_button.configure(state='normal' if child_positions else 'disabled')
                sibling_button.configure(state='normal' if sibling_positions else 'disabled')
                branch_status.set(f"Branch: {len(child_positions)} direct child(ren) · {len(sibling_positions)} sibling(s) · ancestor path {len(relation['lineage'])} · {', '.join(relation['warnings']) or 'INDEXED_PARENT_ID_VERIFIED'}")
                pane.configure(state='normal')
                pane.delete('1.0','end')
                pane.insert('end',f"{data['title']}\nSource: {data['source_file']}\nRevision: {data['revision']}\nIntegrity: {data['integrity']}\n\n")
                for row in result['context']:
                    pane.insert('end',f"[{row['position']+1}/{result['count']}] [{row['role']}] {row['id']}\nParent: {row['parent']}\n")
                    begin=pane.index('end-1c')
                    pane.insert('end',row['text'])
                    end=pane.index('end-1c')
                    if row['selected']:
                        pane.tag_add('selected',begin,end)
                        for first,last in row['highlight_spans']:
                            pane.tag_add('highlight',f'{begin}+{first}c',f'{begin}+{last}c')
                        pane.see(begin)
                    pane.insert('end','\n\n')
                pane.configure(state='disabled')
                location.set(f"Message {result['index']+1}/{result['count']} · exact message ID · contextual ±2")
                previous.configure(state='normal' if result['has_previous'] else 'disabled')
                following.configure(state='normal' if result['has_next'] else 'disabled')
            def move(delta):
                nonlocal index
                index=max(0,min(len(data['messages'])-1,index+delta))
                render()
            def go_parent():
                relation=branch_context(data,index,graph=graph)
                if relation['parent'] is not None:
                    jump(relation['parent'])
            def jump(target):
                nonlocal index
                index=target
                render()
            def go_choice(selector,relation_key):
                relation=branch_context(data,index,graph=graph)
                positions=relation[relation_key]
                selection=selector.current()
                if 0<=selection<len(positions):
                    jump(positions[selection])
            parent_button.configure(command=go_parent)
            child_button.configure(command=lambda:go_choice(child_choice,'children'))
            sibling_button.configure(command=lambda:go_choice(sibling_choice,'siblings'))
            navigation=tk.Frame(win,bg=BG);navigation.pack(fill='x',padx=8,pady=6)
            previous=tk.Button(navigation,text='Previous message',command=lambda:move(-1))
            previous.pack(side='left')
            following=tk.Button(navigation,text='Next message',command=lambda:move(1))
            following.pack(side='left',padx=8)
            tk.Button(navigation,text='Close',command=win.destroy).pack(side='right')
            win.bind('<Left>',lambda event:move(-1))
            win.bind('<Right>',lambda event:move(1))
            render()
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
        source=self.source_filter.get().strip()
        role=self.role_filter.get()
        def work():
            with ArchiveCatalog(db) as catalog:
                rows=search_filtered(catalog,term,source=source,
                      role='' if role=='Any role' else role,limit=200)
            def finish():
                self.search_rows=rows
                self.last_search_term=term
                self.show(self.matches,rows)
                for child in self.search_list.get_children():
                    self.search_list.delete(child)
                for idx,row in enumerate(rows):
                    self.search_list.insert('','end',iid=str(idx),
                        values=(row['title'],row['role'],row['source'],row['snippet']))
                self.tabs.select(self.hits_tab)
            self.after(0,finish)
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
