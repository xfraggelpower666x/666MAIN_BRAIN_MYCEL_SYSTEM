"""R07 explainable local lyrics-text intelligence, never audio inference."""
import collections,re
WORD=re.compile(r"[^\W_]+(?:['’][^\W_]+)*",re.UNICODE)
SECTION=re.compile(r"^\s*\[\s*(intro|verse|pre[- ]?chorus|chorus|hook|bridge|break|drop|outro|refrain|instrumental)(?:\s+\d+)?\s*\]\s*$",re.I)
STOPS=set("the and you your with that this from have will are for but not was were into just here there when what eine einer einem einen nicht und der die das ist ich wir du dein mein mit auf für von ein aus zum zur den dem wie sich noch nur auch aber".split())
def metrics(text):
 if not isinstance(text,str):raise ValueError("Text muss eine Zeichenkette sein")
 lines=[s.strip() for s in text[:250000].splitlines() if s.strip()]
 sections=[];lyrics=[]
 for i,line in enumerate(lines):
  match=SECTION.match(line)
  if match:sections.append({"name":match.group(1).lower().replace(" ","-"),"line":i+1})
  elif not line.startswith("#") and not line.startswith(chr(96)*3):lyrics.append(line)
 tokens=[x.lower() for x in WORD.findall(" ".join(lyrics))]
 words=collections.Counter(w for w in tokens if len(w)>2 and w not in STOPS)
 normalized=collections.Counter(re.sub(r"\s+"," ",s).casefold() for s in lyrics if len(s)>=8)
 repeats=[]
 for line,count in normalized.most_common(12):
  if count>1:
   original=next(s for s in lyrics if re.sub(r"\s+"," ",s).casefold()==line)
   repeats.append({"line":original[:140],"count":count})
 return {"line_count":len(lyrics),"word_count":len(tokens),"unique_words":len(set(tokens)),"section_count":len(sections),
 "sections":sections[:100],"repeat_lines":repeats[:8],
 "top_terms":[{"term":word,"count":count} for word,count in words.most_common(12)],
 "avg_words_per_line":round(len(tokens)/len(lyrics),2) if lyrics else 0,
 "longest_line_chars":max(map(len,lyrics),default=0),
 "caveat":"Textmerkmale; keine Emotion-, Klang-, BPM- oder Audioanalyse."}
def analyze_record(conn,rid):
 if not isinstance(rid,str) or not re.fullmatch("[0-9a-f]{64}",rid):raise ValueError("Ungültige Datensatz-ID")
 row=conn.execute("SELECT id,title,project,category,source_name,source_hash,content,archived FROM records WHERE id=?",(rid,)).fetchone()
 if row is None:raise ValueError("Datensatz nicht vorhanden")
 return {"id":row["id"],"title":row["title"],"project":row["project"],"category":row["category"],
 "source_name":row["source_name"],"source_hash":row["source_hash"],"archived":bool(row["archived"]),"metrics":metrics(row["content"])}
def compare_records(conn,ids):
 if not isinstance(ids,list) or len(ids)!=2 or ids[0]==ids[1]:raise ValueError("Zwei verschiedene Datensätze auswählen")
 items=[analyze_record(conn,rid) for rid in ids]
 terms=[set(x["term"] for x in item["metrics"]["top_terms"]) for item in items]
 return {"items":items,"shared_top_terms":sorted(terms[0]&terms[1]),"comparison_type":"Deskriptiver Textvergleich; kein Plagiats- oder Qualitätsurteil"}
def project_insights(conn):
 rows=conn.execute("SELECT project,category,archived,COUNT(*) n,COUNT(DISTINCT source_name) sources FROM records GROUP BY project,category,archived").fetchall()
 out={}
 for row in rows:
  p=out.setdefault(row["project"],{"project":row["project"],"active":0,"archived":0,"categories":{},"sources":0})
  count=int(row["n"]);p["archived" if row["archived"] else "active"]+=count
  if not row["archived"]:p["categories"][row["category"]]=p["categories"].get(row["category"],0)+count
  p["sources"]+=int(row["sources"])
 return sorted(out.values(),key=lambda p:(-p["active"],p["project"]))
