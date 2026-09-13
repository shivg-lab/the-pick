'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { ArrowUpRight, ArrowRight, MapPin, SlidersHorizontal, Check, ChevronDown, CircleAlert, Compass, Users, Sparkles, X, LoaderCircle, ShieldCheck, Clock, Radio } from 'lucide-react';
import type { Activity, Filters, Providers, Recommendation, Results } from '@/lib/types';
import { api, Job } from '@/lib/api';
import { BRAND } from '@/lib/brand';
import { FieldArt } from '@/components/FieldArt';
import { Preferences } from '@/components/Preferences';
import { EventCard, Guide } from '@/components/ResultViews';

const FAMILY_QUERY = 'I’m in San Jose with two children, have a total budget of $120, want something nearby and prefer vegetarian food options.';
const ICONIC_QUERY = 'I want the most exciting, iconic Bay Area sports experience. Budget and distance do not matter.';
const defaults: Filters = { location: 'San Jose', radius_miles: null, sports: [], teams: [], budget: null, budget_type: 'total', adults: 2, children: 0, family_friendly: false, atmosphere: 'any', local_openness: true, dietary: [], dietary_required: false, accessibility: [], first_time: false };
const family: Filters = { ...defaults, radius_miles: 25, budget: 120, children: 2, family_friendly: true, atmosphere: 'relaxed', dietary: ['vegetarian'] };

export default function Home() {
 const [query,setQuery]=useState(FAMILY_QUERY);
 const [filters,setFilters]=useState<Filters>(family);
 const [dirty,setDirty]=useState<Partial<Filters>>({});
 const [preset,setPreset]=useState<'family'|'iconic'|null>('family');
 const [expanded,setExpanded]=useState(false);
 const [searchedDraft,setSearchedDraft]=useState('');

 const [providers,setProviders]=useState<Providers|null>(null);
 const [providerError,setProviderError]=useState(false);
 const [showStatus,setShowStatus]=useState(false);
 const [mode,setMode]=useState<'auto'|'agent'|'fallback'>('auto');
 const [loading,setLoading]=useState(false);
 const draft=JSON.stringify({query,filters,preset,mode,dirty});
 const [activity,setActivity]=useState<Activity[]>([]);
 const [results,setResults]=useState<Results|null>(null);
 const [guideTab,setGuideTab]=useState('essentials');
 const [guide,setGuide]=useState<Recommendation|null>(null);
 const [error,setError]=useState('');
 const [elapsed,setElapsed]=useState(0);
 const [showExclusions,setShowExclusions]=useState(false);
 const generation=useRef(0);
 const resultRef=useRef<HTMLElement>(null);
 const triggerRef=useRef<HTMLElement|null>(null);
 const getStatus=useCallback(async()=>{try{setProviders(await api<Providers>('/api/providers'));setProviderError(false);}catch{setProviderError(true);}},[]);
 useEffect(()=>{getStatus();},[getStatus]);
 useEffect(()=>{if(!loading)return;setElapsed(0);const t=setInterval(()=>setElapsed(v=>v+1),1000);return()=>clearInterval(t);},[loading]);
 useEffect(()=>{if(!guide)return;const overflow=document.body.style.overflow;document.body.style.overflow='hidden';const handler=(e:KeyboardEvent)=>{if(e.key==='Escape')setGuide(null);if(e.key==='Tab'){const elements=Array.from(document.querySelectorAll<HTMLElement>('.guide-panel button,.guide-panel a,.guide-panel input')).filter(el=>el.offsetParent!==null);const first=elements[0],last=elements[elements.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}};document.addEventListener('keydown',handler);return()=>{document.body.style.overflow=overflow;document.removeEventListener('keydown',handler);triggerRef.current?.focus();};},[guide]);
 function update<K extends keyof Filters>(key:K,value:Filters[K]) {setFilters(f=>({...f,[key]:value}));setDirty(d=>({...d,[key]:value}));}
 function choose(name:'family'|'iconic') {setPreset(name);setQuery(name==='family'?FAMILY_QUERY:ICONIC_QUERY);setFilters(name==='family'?family:{...defaults,atmosphere:'iconic'});setDirty({});setError('');}
 async function search() {
  if(loading||query.trim().length<3)return;
  const current=++generation.current;
  setSearchedDraft(draft);setExpanded(false);setShowExclusions(false);
  setLoading(true);setResults(null);setActivity([]);setError('');
  setTimeout(()=>resultRef.current?.scrollIntoView({behavior:'smooth',block:'start'}),50);
  try {
   // Only edited form fields override natural-language extraction in agent mode.
   const submitted=mode==='fallback'?filters:dirty;
   const {request_id}=await api<{request_id:string}>('/api/jobs',{method:'POST',body:JSON.stringify({query,filters:submitted,preset,mode})});
   const started=Date.now();
   while(current===generation.current) {
    const job=await api<Job>(`/api/jobs/${request_id}`);
    setActivity(job.activity);
    if(job.status==='complete'&&job.result){setResults(job.result);break;}
    if(job.status==='failed')throw new Error(job.error);
    if(Date.now()-started>600000)throw new Error('The local investigation is taking longer than expected. Check Ollama, then retry.');
    await new Promise(resolve=>setTimeout(resolve,1000));
   }
  }catch(e){setError(e instanceof Error?e.message:'Something went wrong. Please retry.');}
  finally{if(current===generation.current)setLoading(false);getStatus();}
 }
 function editPreferences() {setExpanded(true);requestAnimationFrame(()=>document.getElementById('preferences')?.scrollIntoView({behavior:'smooth',block:'start'}));}
 function openGuide(r:Recommendation, tab='essentials') {setGuideTab(tab);triggerRef.current=document.activeElement as HTMLElement;setGuide(r);}
 const stateLabel=providerError?'Backend unavailable':!providers?'Checking local model':providers.agent_ready?'Local agent ready':'Setup needed';
 return <>
  <div className="topline"><span>A GOOD DAY STARTS WITH A GREAT PICK.</span><span>BAY AREA, CA <span className="tiny-dot"/> 37.34° N · 121.89° W</span></div>
  <header className="site-header"><a href="/" className="wordmark" aria-label="The Pick home">{BRAND.name.toLowerCase()}<span>↗</span></a><nav aria-label="Main navigation"><a href="#discover">Discover</a><a href="#how-it-works">How it works</a><button className="status-button" onClick={()=>setShowStatus(v=>!v)}><span className={`status-dot ${providers?.agent_ready&&!providerError?'ready':''}`}/>{stateLabel}<ChevronDown size={13}/></button></nav></header>
  {showStatus&&<div className="provider-panel"><div><h3>Your local concierge</h3><button className="icon-button" onClick={()=>setShowStatus(false)} aria-label="Close provider status"><X size={18}/></button></div><p>Ollama: {providers?.ollama.reachable?'Connected':'Unavailable'} · Chat: {providers?.chat_model||'qwen3:8b'} · {providers?.documents||0} source documents</p><p>Semantic index: {providers?.vector_ready?'Ready':'Run ingestion'} · No cloud model or sports API key required for the demo.</p>{(!providers?.agent_ready||providerError)&&<pre>ollama serve{'\n'}ollama pull qwen3:8b{'\n'}ollama pull embeddinggemma{'\n'}cd backend && uv run python -m scripts.ingest{'\n'}uv run uvicorn app.main:app --port 8000</pre>}<button className="text-button" onClick={getStatus}>Recheck connection <ArrowRight size={15}/></button></div>}
  <main>
   <section className={`hero ${results||loading?'hero-compact':''}`} id="discover"><div className="hero-copy"><div className="eyebrow"><span className="tiny-dot"/> YOUR PERSONAL LIVE-SPORTS CONCIERGE</div><h1>Go for <br/>the <span>experience.</span></h1><p>The big rivalry. The little ballpark. The afternoon they’ll talk about all week. Find the game worth showing up for—and know before you go.</p><div className="hero-bottom"><div className="mini-avatars"><span>↗</span><span>✳</span><span>◎</span></div><span>Big leagues. Local favorites.<br/><strong>One pick that feels like you.</strong></span></div></div><div className="hero-visual"><FieldArt hero/><div className="hero-ticket"><div><span>ADMIT YOUR WHOLE CREW</span><b>Less searching.<br/>More showing up.</b></div><div className="ticket-stub"><Compass size={30}/><small>THE<br/>BAY AREA</small></div></div><span className="hero-edition">THE BAY AREA EDITION — NO. 001</span></div></section>
   <div className="outing-workspace">
   <Preferences filters={filters} expanded={expanded} loading={loading} mode={mode} onMode={setMode} update={update} onExpand={()=>setExpanded(v=>!v)} onSearch={search} canSearch={!loading&&query.trim().length>=3}/>
   <div className="outing-content">
   <section className="search-section" aria-labelledby="search-title"><div className="search-heading"><h2 id="search-title">What’s your kind of game day?</h2><span><span className="tiny-dot"/> DISCOVER → DECIDE → PREPARE</span></div>
    <div className="search-box"><div className="query-row"><Sparkles size={23}/><label className="sr-only" htmlFor="query">Describe your ideal outing</label><textarea disabled={loading} id="query" value={query} maxLength={2000} onChange={e=>{setQuery(e.target.value);setPreset(null);}} placeholder="Tell us where you are, who’s coming, and what makes a great day…" rows={2}/><button className="button orange find-button" onClick={search} disabled={loading||query.trim().length<3}>{loading?'Investigating':results&&draft!==searchedDraft?'Update my pick':'Find my pick'}{loading?<LoaderCircle className="spin" size={18}/>:<ArrowUpRight size={20}/>}</button></div>
    </div><div className="presets"><span>TRY A DIFFERENT KIND OF DAY</span><button className={preset==='family'?'selected':''} onClick={()=>choose('family')} disabled={loading}><Users size={15}/>Family day, on a budget <ArrowUpRight size={14}/></button><button className={preset==='iconic'?'selected':''} onClick={()=>choose('iconic')} disabled={loading}><Radio size={15}/>The iconic Bay Area experience <ArrowUpRight size={14}/></button></div>
    <p className="data-note"><ShieldCheck size={14}/>Illustrative seasonal sampler · 8 curated scenarios, not live listings. Venue information is sourced separately.</p>
   </section>
   <section className="results-section" ref={resultRef} aria-live="polite" aria-busy={loading}>
    {results&&draft!==searchedDraft&&<div className="stale-results" role="status"><CircleAlert size={18}/><span>Your preferences have changed. These picks reflect your previous search.</span><button className="button dark" onClick={search}>Update my pick <ArrowRight size={16}/></button></div>}
    {error&&<div className="error-state"><CircleAlert size={28}/><h2>We hit a pause in play.</h2><p>{error}</p><button className="button dark" onClick={search}>Try again <ArrowRight size={17}/></button><button className="text-button" onClick={()=>{setMode('fallback');setExpanded(true);}}>Choose non-agent fallback</button></div>}
    {loading&&<div className="investigation"><div className="radar"><Compass size={43}/></div><span className="eyebrow">A LITTLE RESEARCH. A BETTER DAY.</span><h2>Finding your kind of game.</h2><p>Your concierge is checking the details that make the difference.</p><div className="live-trace">{activity.map((a,i)=><div key={i}>{a.status==='warning'?<CircleAlert size={16}/>:<Check size={16}/>}<span>{a.step}</span></div>)}<div><LoaderCircle size={16} className="spin"/><span>{activity.length?'Considering the next step…':'Connecting to the local concierge…'}</span></div></div><small>{elapsed}s elapsed · Local inference can take a minute or two. Activity reflects completed work.</small></div>}
    {results&&<><div className={`mode-notice ${results.agent_active?'':'fallback'}`}><span>{results.agent_active?<Sparkles size={17}/>:<CircleAlert size={17}/>}<strong>{results.agent_active?'Investigated by your local Ollama agent':'Fallback mode—agent reasoning is unavailable.'}</strong></span><small>{results.agent_active?`${results.retrieval_mode} · real semantic retrieval`:'Structured presets and template explanations · not an agent demonstration'}</small></div><div className="section-heading results-heading"><div><span className="eyebrow">YOUR DAY, SHORTLISTED</span><h2>{results.recommendations.length?'One pick. Your kind of day.':'No compromises on your must-haves.'}</h2></div><div className="result-count"><b>{results.candidates_considered}</b> considered <span>→</span> <b>{results.recommendations.length}</b> worth a closer look</div></div><div className="intent-summary"><MapPin size={14}/>{results.parsed_intent.location}<span>·</span>{results.parsed_intent.adults+results.parsed_intent.children} people<span>·</span>{results.parsed_intent.budget===null?'Open budget':`$${results.parsed_intent.budget} budget`}<span>·</span>{results.parsed_intent.radius_miles===null?'No distance limit':`${results.parsed_intent.radius_miles} mi radius`}<button onClick={editPreferences}>Edit preferences <SlidersHorizontal size={13}/></button></div>
    {results.recommendations.length?<div className="recommendation-stack"><EventCard intent={results.parsed_intent} key={results.recommendations[0].event.id} item={results.recommendations[0]} primary onGuide={tab=>openGuide(results.recommendations[0],tab)}/>{results.recommendations.length>1&&<section className="alternatives-section" aria-labelledby="alternatives-title"><div className="alternatives-heading"><div><span className="eyebrow">A DIFFERENT WAY TO SPEND THE DAY</span><h3 id="alternatives-title">Also worth showing up for.</h3></div><span>{results.recommendations.length-1} strong alternatives</span></div><div className="event-grid">{results.recommendations.slice(1).map(r=><EventCard intent={results.parsed_intent} key={r.event.id} item={r} onGuide={tab=>openGuide(r,tab)}/>)}</div></section>}</div>:<div className="empty-state"><Compass size={40}/><h3>No qualifying events in this small sampler.</h3><p>Try a wider radius, a different date range or a larger budget. A required dietary or accessibility need also needs verified evidence.</p><button className="button dark" onClick={editPreferences}>Adjust preferences <ArrowRight size={16}/></button></div>}
    <div className="results-meta"><span><Clock size={14}/>Investigated in {(results.processing_ms/1000).toFixed(1)}s · {new Date(results.created_at).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'})}</span><button className="text-button" onClick={()=>setShowExclusions(v=>!v)}>{results.exclusions.length} excluded · see why <ChevronDown size={14}/></button></div>
    {showExclusions&&<div className="exclusions">{results.exclusions.map(e=><div key={e.event_id}><X size={15}/><b>{e.name}</b><span>{e.reason}</span></div>)}</div>}
    <details className="activity-details"><summary><Sparkles size={16}/>Behind your pick · investigation & transparency<ChevronDown size={15}/></summary><div className="activity-body"><div>{results.activity.map((a,i)=><p key={i}>{a.status==='warning'?<CircleAlert size={15}/>:<Check size={15}/>} {a.step}</p>)}</div><div><h4>What to keep in mind</h4>{results.warnings.map(w=><p key={w}>{w}</p>)}</div></div></details>
    </>}
   </section>
   {!results&&!loading&&<section className="editorial"><div className="section-heading"><div><span className="eyebrow">THERE’S MORE THAN ONE WAY TO BE A FAN</span><h2>The Bay has range.</h2></div><span className="editorial-note">A glimpse of our illustrative sampler <ArrowDownRight/></span></div><div className="editorial-grid">{[{sport:'baseball',color:'orange',title:'Small park. Big memories.',sub:'SAN JOSE GIANTS · EXCITE BALLPARK',tag:'THE LOCAL FAVORITE',preset:'family' as const},{sport:'football',color:'navy',title:'Some games mean more.',sub:'CAL × STANFORD · THE BIG GAME',tag:'THE BAY AREA TRADITION',preset:'iconic' as const},{sport:'soccer',color:'red',title:'A whole new home crowd.',sub:'BAY FC · PAYPAL PARK',tag:'THE NEXT CHAPTER',preset:'iconic' as const}].map(e=><button className="editorial-card" key={e.title} onClick={()=>{choose(e.preset);document.getElementById('search-title')?.scrollIntoView({behavior:'smooth'});}}><div className="editorial-image"><FieldArt sport={e.sport} variant={e.color}/><span>{e.tag}</span><div className="round-arrow"><ArrowUpRight size={23}/></div></div><small>{e.sub}</small><h3>{e.title}</h3></button>)}</div></section>}
   </div></div>
   <section className="how-it-works" id="how-it-works"><div className="how-title"><span className="eyebrow">MORE THAN AN EVENT LIST</span><h2>We do the homework.<br/>You make the memories.</h2></div><div className="how-steps">{[['01','Discover','Tell us what a good day looks like. Your local agent investigates the events that could fit.'],['02','Decide','See the best fit, two alternatives and the tradeoffs. Every score has a breakdown.'],['03','Prepare','Bags, food, parking and seating, plus what-to-wear tips. Prepare for the whole outing, with unknowns clearly marked.']].map(([n,t,d])=><div key={n}><span>{n}</span><h3>{t}<ArrowUpRight size={20}/></h3><p>{d}</p></div>)}</div></section>
  </main><footer className="site-footer"><a href="/" className="wordmark">{BRAND.name.toLowerCase()}<span>↗</span></a><p>Find the game worth showing up for.</p><span>MADE FOR THE BAY. BUILT AROUND YOU.</span></footer>
  {guide&&results&&<Guide initialTab={guideTab} item={guide} requestId={results.request_id} onClose={()=>setGuide(null)}/>}
 </>;
}
function ArrowDownRight(){return <ArrowUpRight size={16} style={{transform:'rotate(90deg)'}}/>;}
