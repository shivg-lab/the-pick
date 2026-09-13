"""Generate the editable architecture artwork; render its SVG with Sharp."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent
parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1700" viewBox="0 0 2400 1700">
<defs>
 <marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto-start-reverse"><path d="M0 0 L9 4.5 L0 9" fill="none" stroke="#62736d" stroke-width="1.5"/></marker>
 <marker id="optional" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9" fill="none" stroke="#b17742" stroke-width="1.5"/></marker>
</defs>
<rect width="2400" height="1700" fill="#f7f5ee"/>
<g font-family="Arial, Helvetica, sans-serif" fill="#20352f">''']

def box(x,y,w,h,fill='#fffef9',stroke='#cdd5c8',radius=22,dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ''
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"{extra}/>')

def text(x,y,value,size=28,color='#20352f',weight=400):
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>')

def lines(x,y,values,size=27,gap=42,color='#52665b'):
    for i,value in enumerate(values): text(x,y+i*gap,value,size,color)

def path(d,both=False,dashed=False):
    parts.append(f'<path d="{d}" fill="none" stroke="{"#b17742" if dashed else "#62736d"}" stroke-width="3" stroke-linejoin="round" marker-end="url(#{"optional" if dashed else "arrow"})"' + (' marker-start="url(#arrow)"' if both else '') + (' stroke-dasharray="10 9"' if dashed else '') + '/>')

def tag(x,y,value,color='#52665b'): text(x,y,value,21,color,700)

text(70,100,'the pick',66,weight=800)
text(315,100,'↗',70,'#ea6a2b',700)
text(440,99,'Application architecture',52,weight=700)
text(72,151,'A local sports concierge that connects discovery, evidence, ranking and venue preparation.',29,'#52665b')
box(40,205,2320,1125,fill='#eef1e7',stroke='#c4d0bf',radius=28)
tag(72,243,'CURRENT LOCAL DEMO  /  ONE MACHINE')

# Backend boundary and component cards.
box(620,265,1020,1035,fill='#e5ebde',stroke='#becbb5')
tag(646,291,'PYTHON BACKEND / REQUEST WORKFLOW')
box(670,320,920,175)
tag(700,355,'API & JOB CONTROL')
text(700,400,'FastAPI + Pydantic',37,weight=700)
lines(700,442,['Validated requests · progress polling · saved results','One investigation at a time; busy requests receive HTTP 429'],25,34)

box(670,580,920,260,fill='#203b34',stroke='#203b34')
tag(700,618,'AGENT ORCHESTRATION','#ffb47c')
text(700,661,'Plan → execute tools → observe',39,'#ffffff',700)
lines(700,709,['Quote-grounded intent → bounded investigation','Validated source-ID selection for explanations'],28,42,'#e0e9db')
text(700,806,'Limits: 4 planning iterations · 10 total tool calls',25,'#ffceaa')

box(670,945,920,310)
tag(700,985,'APPLICATION TOOLS & DETERMINISTIC RULES')
for x in [975,1280]: parts.append(f'<path d="M{x} 1010 V1224" stroke="#d8dfd1" stroke-width="2"/>')
text(700,1048,'Inventory',30,weight=700)
lines(700,1092,['8 demo scenarios','Event / sports data','Eligibility & filters','Distance & costs'],25,40)
text(1004,1048,'Ranking',30,weight=700)
lines(1004,1092,['Fixed score weights','Evidence confidence','Hard needs checks','Top 3 + tradeoffs'],25,40)
text(1308,1048,'Visitor guide',30,weight=700)
lines(1308,1092,['Bags · food · arrival','Parking · seating','Weather · attire','Sources · conflicts'],25,40)

# Browser and durable storage.
box(90,335,440,310)
tag(120,374,'USER EXPERIENCE')
text(120,426,'Next.js + React',36,weight=700)
text(120,465,'TypeScript · Tailwind CSS',24,'#52665b')
lines(120,512,['Describe an outing','Compare recommendations','Read guides & give feedback'],25,42)
box(90,995,440,255)
tag(120,1034,'DURABLE LOCAL STORAGE')
text(120,1085,'SQLite',39,weight=700)
lines(120,1131,['Completed recommendations','User feedback','WAL-backed persistence'],25,40)

# Local model server, separate from the backend process.
box(1770,320,520,310)
tag(1800,358,'LOCAL MODEL SERVER')
text(1800,408,'Ollama',40,weight=700)
text(1800,455,'qwen3:8b',30,weight=700)
text(1800,490,'Intent, tool plans, source selection',24,'#52665b')
text(1800,543,'embeddinggemma',30,weight=700)
text(1800,580,'Query & document embeddings',24,'#52665b')

box(1770,820,520,435)
tag(1800,860,'BACKEND RETRIEVAL + LOCAL FILES')
text(1800,910,'RAG evidence retrieval',34,weight=700)
lines(1800,956,['NumPy cosine search · JSON index','Venue / event metadata filters','Source IDs, dates and freshness'],24,38)
parts.append('<path d="M1800 1060 H2260" stroke="#d8dfd1" stroke-width="2"/>')
text(1800,1106,'Curated official-source corpus',28,weight=700)
lines(1800,1148,['64 stored documents','Venue rules · food · sports history','Manual curation and ingestion'],24,37)

# Connections, separated from the text-bearing regions.
path('M530 409 H670')
text(548,389,'request',19,'#52665b')
path('M670 455 H530')
text(540,485,'results',19,'#52665b')
path('M1130 495 V580',both=True)
text(1150,545,'jobs + activity',21,'#52665b')
path('M1130 840 V945',both=True)
text(1150,895,'typed tools + observations',21,'#52665b')
path('M710 495 V525 H582 V1120 H530',both=True)
text(96,938,'Snapshots and feedback survive restarts.',22,'#52665b')
path('M1590 705 H1685 V465 H1770',both=True)
text(1652,676,'chat',21,'#52665b')
path('M2030 630 V820',both=True)
text(2050,723,'embeddings',22,'#52665b')
path('M1590 1090 H1770',both=True)
text(1620,1069,'evidence',21,'#52665b')

# Optional services remain outside the current machine boundary.
box(620,1415,1020,185,fill='#fcf0e2',stroke='#c99b68',dash='9 7')
tag(650,1453,'OPTIONAL HYBRID ADAPTERS  /  NOT CONFIGURED IN THIS DEMO','#9a602f')
text(650,1502,'Ticketmaster  +  Sportradar  +  curated events',33,weight=700)
text(650,1547,'Live listings / sports data require provider setup and reviewed enrichment.',25,'#775e43')
path('M1130 1415 V1255',dashed=True)
text(1150,1380,'hybrid mode',22,'#9a602f')

tag(90,1452,'FALLBACK PATH')
lines(90,1495,['Structured presets + templates','Lexical retrieval; visibly labeled','as a non-agent fallback.'],24,38)
tag(1770,1452,'DEMO BOUNDARIES')
lines(1770,1495,['Dates and prices are illustrative.','Venue evidence is stored locally.','No cloud model is required.'],24,38)
text(1770,1610,'Live weather: Open-Meteo (optional)',24,'#52665b')
text(72,1663,'Implementation view · Next.js :3000 · FastAPI :8000 · Ollama :11434',23,'#52665b')
text(1770,1663,'Discover → Decide → Prepare',25,'#20352f',700)
parts.append('</g></svg>')
(OUT/'the-pick-architecture.svg').write_text('\n'.join(parts))
print(OUT/'the-pick-architecture.svg')
