"""R5.5 optional Tk tree window; no source/database mutation."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from archive_branch_tree import project_branch_tree, tree_ancestry, describe_tree_node, search_branch_tree

PAGE = 120


def open_branch_tree_window(owner, conversation, selected_index, on_jump):
    """Visualize every indexed message by lazily expanded verified parent links.

    The callback navigates the existing conversation viewer; this is a companion
    window rather than a second database, importer or router.
    """
    projection = project_branch_tree(conversation)
    messages = conversation['messages']
    window = tk.Toplevel(owner)
    window.title('666 ChatBackup · Indexed conversation branches · READ ONLY')
    window.geometry('1100x680')
    window.configure(bg='#090f1b')
    summary = tk.StringVar(value=f"{projection['count']} indexed messages · {len(projection['roots'])} visual roots · {projection['status']} · NO SOURCE WRITES")
    tk.Label(window, textvariable=summary, bg='#090f1b', fg='#00e8ff', anchor='w').pack(fill='x', padx=12, pady=8)
    searchbar = tk.Frame(window, bg='#090f1b')
    searchbar.pack(fill='x', padx=12, pady=(0, 6))
    tk.Label(searchbar, text='Find message ID or text:',
             fg='#00e8ff', bg='#090f1b').pack(side='left')
    search_term = tk.StringVar()
    search_entry = tk.Entry(searchbar, textvariable=search_term, width=38)
    search_entry.pack(side='left', fill='x', expand=True, padx=8)
    search_status = tk.StringVar(value='Exact indexed message search · read only')
    tk.Label(window, textvariable=search_status, fg='#ff2acb',
             bg='#090f1b', anchor='w').pack(fill='x', padx=12)
    frame = tk.Frame(window, bg='#10192a')
    frame.pack(fill='both', expand=True, padx=12, pady=4)
    tree = ttk.Treeview(frame, columns=('role','preview','children','warning'), show='tree headings',
                        selectmode='browse')
    tree.heading('#0', text='Exact indexed message ID')
    tree.column('#0', width=285, minwidth=120)
    for name,label,width in [('role','Role',90),('preview','Message preview',440),
                              ('children','Children',75),('warning','Relationship warning',205)]:
        tree.heading(name, text=label)
        tree.column(name, width=width, minwidth=60)
    ybar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=ybar.set)
    ybar.pack(side='right', fill='y')
    tree.pack(side='left', fill='both', expand=True)

    def child_positions(parent):
        return projection['roots'] if parent is None else projection['children'][parent]

    def node_id(pos):
        return f'm:{pos}'

    def add_page(parent_id, parent_pos, start):
        positions = child_positions(parent_pos)
        end = min(start + PAGE, len(positions))
        for pos in positions[start:end]:
            item = describe_tree_node(conversation, projection, pos)
            warning = ', '.join(item['warnings'])
            tree.insert(parent_id,'end',iid=node_id(pos), text=item['id'],
                        values=(item['role'],item['preview'],item['children'],warning))
            if item['children']:
                tree.insert(node_id(pos),'end',iid=f'placeholder:{pos}',text='Expand to load direct replies')
        if end < len(positions):
            marker = f'more:{parent_pos if parent_pos is not None else "root"}:{end}'
            tree.insert(parent_id, 'end', iid=marker,
                        text=f'Load next {min(PAGE,len(positions)-end)} messages…',
                        values=('','More results','',f'{end}/{len(positions)} shown'))

    def load_more(marker):
        _, value, offset = marker.split(':',2)
        parent_pos = None if value == 'root' else int(value)
        parent_id = '' if parent_pos is None else node_id(parent_pos)
        tree.delete(marker)
        add_page(parent_id,parent_pos,int(offset))

    def expand(event=None):
        current = tree.focus()
        if not current.startswith('m:'):
            return
        pos = int(current[2:])
        placeholder = f'placeholder:{pos}'
        if tree.exists(placeholder):
            tree.delete(placeholder)
            add_page(current,pos,0)

    def selected_position():
        selected = tree.selection()
        if not selected:
            return None
        current = selected[0]
        if current.startswith('more:'):
            load_more(current)
            return None
        return int(current[2:]) if current.startswith('m:') else None

    def jump(event=None):
        pos = selected_position()
        if pos is not None:
            on_jump(pos)
            owner.lift()
            summary.set(f"Selected {pos+1}/{projection['count']} · {messages[pos]['id']} · {projection['status']}")

    def ensure_loaded(parent_pos, target_pos):
        parent_id = '' if parent_pos is None else node_id(parent_pos)
        while not tree.exists(node_id(target_pos)):
            marker = next((child for child in tree.get_children(parent_id)
                           if child.startswith('more:')),None)
            if marker is None:
                break
            load_more(marker)
        return tree.exists(node_id(target_pos))

    def reveal(position):
        parent = None
        for pos in tree_ancestry(projection,position):
            if parent is not None:
                pid = node_id(parent)
                expand_node(pid)
                tree.item(pid,open=True)
            if not ensure_loaded(parent,pos):
                return
            parent=pos
        item=node_id(position)
        tree.selection_set(item)
        tree.focus(item)
        tree.see(item)

    def expand_node(item):
        pos=int(item[2:])
        placeholder=f'placeholder:{pos}'
        if tree.exists(placeholder):
            tree.delete(placeholder)
            add_page(item,pos,0)

    search_offset = 0
    search_total = 0
    search_page_size = 200

    def search_tree(reset=True):
        nonlocal search_offset, search_total
        query = search_term.get().strip()
        if reset:
            search_offset = 0
        try:
            result = search_branch_tree(conversation, projection, query,
                                        limit=search_page_size, offset=search_offset)
        except ValueError as exc:
            search_status.set(str(exc))
            return
        search_total = result['total']
        for item in hits.get_children():
            hits.delete(item)
        for row in result['matches']:
            hits.insert('', 'end', iid=f'hit:{row["position"]}',
                        values=(row['id'], row['role'], row['preview'],
                                ' / '.join(str(n+1) for n in row['path']),
                                ', '.join(row['warnings'])))
        search_status.set(
            f'{search_total} match(es) · showing '
            f'{search_offset + (1 if result["matches"] else 0)}–'
            f'{search_offset + len(result["matches"])}'
        )
        prev_button.configure(state='normal' if search_offset else 'disabled')
        next_button.configure(state='normal' if result['has_more'] else 'disabled')
        if result['matches']:
            hits.selection_set(f'hit:{result["matches"][0]["position"]}')

    def turn_search_page(direction):
        nonlocal search_offset
        next_offset = max(0, search_offset + direction * search_page_size)
        if direction > 0 and next_offset >= search_total:
            return
        search_offset = next_offset
        search_tree(reset=False)

    def open_search_hit(event=None):
        selected = hits.selection()
        if not selected:
            return
        pos = int(selected[0].split(':', 1)[1])
        reveal(pos)
        on_jump(pos)
        owner.lift()

    tree.bind('<<TreeviewOpen>>',expand)
    tree.bind('<Double-1>',jump)
    bar = tk.Frame(window,bg='#090f1b');bar.pack(fill='x',padx=12,pady=8)
    tk.Button(bar,text='Jump to selected message',command=jump).pack(side='left')
    tk.Button(bar,text='Show original selected message',command=lambda:reveal(selected_index)).pack(side='left',padx=8)
    tk.Button(bar,text='Close tree',command=window.destroy).pack(side='right')
    tk.Button(searchbar, text='Search tree', command=search_tree).pack(side='left')
    search_entry.bind('<Return>', lambda event: search_tree())
    prev_button = tk.Button(searchbar, text='◀', state='disabled',
                            command=lambda:turn_search_page(-1))
    prev_button.pack(side='left', padx=(8,2))
    next_button = tk.Button(searchbar, text='▶', state='disabled',
                            command=lambda:turn_search_page(1))
    next_button.pack(side='left', padx=(2,0))
    result_frame = tk.Frame(window, bg='#10192a')
    result_frame.pack(fill='x', padx=12, pady=(3,8))
    hits = ttk.Treeview(result_frame, columns=('id','role','preview','path','warnings'),
                        show='headings', height=5, selectmode='browse')
    for col,label,width in [('id','Message ID',205),('role','Role',80),
                            ('preview','Match preview',350),
                            ('path','Verified ancestry',190),('warnings','Warnings',190)]:
        hits.heading(col,text=label)
        hits.column(col,width=width,minwidth=65)
    hits.pack(fill='x', expand=True)
    hits.bind('<Double-1>', open_search_hit)
    tk.Button(window, text='Open selected tree-search result',
              command=open_search_hit).pack(anchor='e',padx=12,pady=(0,5))
    add_page('',None,0)
    reveal(selected_index)
    return window
