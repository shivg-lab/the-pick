'use client';
import { useState } from 'react';
import { ArrowUpRight, MapPin, ArrowRight, ShieldCheck, Check, ShoppingBag, Utensils, Droplets, CircleAlert, X, ThumbsUp, ThumbsDown, ExternalLink, Ticket, ChevronDown, Clock, Accessibility, Ban, RotateCcw } from 'lucide-react';
import type { Recommendation, Results } from '@/lib/types';
import { api, eventDate, eventTime, money, sourceUrl } from '@/lib/api';
import { FieldArt } from './FieldArt';
import { PreparationPreview, PreparationDetails } from './Preparation';
import { fitCopy } from '@/lib/presentation';

const labels: Record<string,string> = { user_fit: 'Your preferences', significance: 'Cultural & competitive significance', experience: 'Experience & atmosphere', convenience: 'Convenience', value: 'Price & value', personal_needs: 'Family, food & accessibility' };
export function ScoreDetails({ item }: { item: Recommendation }) {
 return <details className="score-details"><summary>See how the score adds up <ChevronDown size={16}/></summary><div className="score-explainer"><p>Fixed evidence inputs. Transparent weights. Missing factors are removed and remaining weights are normalized proportionally.</p>{Object.entries(item.score.factors).map(([key,value])=><div className="factor" key={key}><div><span>{labels[key]}</span><b>{value === null ? 'N/A' : Math.round(value)}</b></div><div className="factor-track"><i style={{width:`${value || 0}%`}}/></div><small>{value === null ? 'Unavailable or irrelevant · not scored' : `${Math.round(item.score.weights[key]*100)}% of score`} · {item.score.rationale[key]}</small></div>)}<p>Evidence confidence measures source quality, coverage and freshness separately. Illustrative events are capped at 75% confidence.</p></div></details>;
}
export function GuidePreview({ item, onGuide }: { item: Recommendation; onGuide: (tab?: string) => void }) {
 const { policy, food, arrival } = item.guide;
 const fields = [
  { label:'Your bag', icon:ShoppingBag, evidence:policy.fields.bags, claim:policy.fields.bags?.claim },
  { label:'Outside food', icon:Utensils, evidence:policy.fields.outside_food, claim:policy.fields.outside_food?.claim },
  { label:'Food options', icon:Utensils, evidence:food[0]?.evidence, claim:food[0]?.evidence.claim },
  { label:'Arrival', icon:MapPin, evidence:undefined, claim:arrival[0] },
 ];
 return <section className="guide-preview" aria-label="Venue guide preview"><div className="preview-heading"><div><span className="eyebrow">A LITTLE PREPARATION GOES A LONG WAY</span><h4>Know before you go.</h4></div><button className="text-button" onClick={()=>onGuide()}>Full venue guide <ArrowUpRight size={16}/></button></div>
  <p className="preview-date">Stored guidance · reviewed {policy.last_verified || 'date unavailable'}. Recheck event-specific instructions.</p>
  {policy.conflicts.map(c=><p className="preview-warning" key={c}><CircleAlert size={16}/>{c}</p>)}
  <div className="preview-grid">{fields.map(({ label, icon:Icon, evidence, claim })=><div className="preview-fact" key={label}><Icon size={18}/><h5>{label}</h5><p>{claim || 'Not verified. Check the official venue guide.'}</p>{label==='Food options'&&food.length>0&&<span className="preview-status">{food[0].vegetarian===true?'Vegetarian listed':'Vegetarian unverified'}</span>}{evidence&&<a href={sourceUrl(evidence.source_url)} target="_blank" rel="noreferrer">{evidence.freshness==='stale'?'Stale source · recheck':'Official source'} <ExternalLink size={11}/></a>}</div>)}</div>
  <PreparationPreview item={item} onOpen={()=>onGuide('parking & comfort')}/>
  {(policy.warnings.length>0||item.guide.warnings.length>0)&&<details className="preview-notes"><summary>More details to check <ChevronDown size={14}/></summary>{[...new Set([...policy.warnings,...item.guide.warnings])].map(w=><p key={w}>{w}</p>)}</details>}
 </section>;
}
export function EventCard({ item, intent, primary, onGuide }: { item: Recommendation; intent:Results['parsed_intent']; primary?: boolean; onGuide: (tab?: string) => void }) {
 const e=item.event;
 const copy=fitCopy(item,intent);
 return <article className={`event-card ${primary?'primary-card':'alternative-card'}`}>
  {primary&&<div className="pick-ribbon"><strong><span className="mini-spark">✳</span> THE PICK FOR YOU</strong><span>BIG EXPERIENCES. YOUR BEST FIT.</span></div>}
  <div className="pick-body"><div className="event-art"><FieldArt sport={e.sport} variant={e.color}/><div className="art-top"><span className="label-pill">{primary?e.league:`0${item.rank} / THE ALTERNATIVE`}</span><span className="demo-pill">{e.data_mode.toUpperCase()}</span></div><div className="art-bottom"><span>{e.league} <i/> {e.sport}</span><span>{e.city}</span></div></div>
  <div className="event-content"><div className="event-eyebrow">{eventDate(e.start_time)} <span>·</span> {eventTime(e.start_time)} PT</div><h3>{e.name}</h3><p className="venue-line"><MapPin size={14}/>{e.venue} <span>·</span> {item.distance_miles ?? '—'} mi</p>
   <div className="score-row"><div className="score-number"><b>{Math.round(item.score.opportunity_score)}</b><span>Opportunity<br/>Score <small>/ 100</small></span></div><div className="confidence"><ShieldCheck size={16}/><b>{item.score.evidence_confidence}%</b><span>Evidence confidence</span></div></div>
   <div className="why-section"><h4>{primary?'WHY THIS IS YOUR PICK':'WHY IT’S IN THE RUNNING'}</h4><p>{copy.lead}</p>{primary&&copy.supporting&&<p className="event-context">{copy.supporting}</p>}</div>
   <div className="cost-row"><div><b>{money(e.price_min)}</b><span> / ticket, {e.data_mode==='illustrative'?'illustrative':'listed'}</span></div><small>{money(item.estimated_total)} outing estimate</small></div>
   <button className={primary?'button dark full':'button outline full'} onClick={()=>onGuide()}>Know before you go <ArrowUpRight size={18}/></button>
   {item.tradeoffs[0]&&<div className="tradeoff"><CircleAlert size={14}/><span>{item.tradeoffs[0]}</span></div>}
  </div></div>
  <div className="card-score-details"><ScoreDetails item={item}/></div>
  {primary&&<GuidePreview item={item} onGuide={onGuide}/>}
 </article>;
}
export function Guide({ item, requestId, onClose, initialTab = 'essentials' }: { item: Recommendation; requestId: string; onClose: () => void; initialTab?: string }) {
 const [tab,setTab]=useState(initialTab);
 const [feedback,setFeedback]=useState('');
 const [reason,setReason]=useState('');
 const [correction,setCorrection]=useState('');
 const [saved,setSaved]=useState('');
 const fields=[['bags','Your bag',ShoppingBag],['outside_food','Outside food',Utensils],['water','Water bottles',Droplets],['exceptions','Children & medical needs',Accessibility],['prohibited','Prohibited items',Ban],['reentry','Leaving & re-entry',RotateCcw]] as const;
 async function send(attend: boolean) { try {await api('/api/feedback',{method:'POST',body:JSON.stringify({request_id:requestId,event_id:item.event.id,rating:feedback||null,would_attend:attend,reason,correction})});setSaved('Saved locally. Thanks for helping improve the next outing.');}catch(e){setSaved((e as Error).message);} }
 return <div className="guide-backdrop" onClick={e=>{if(e.target===e.currentTarget)onClose();}}><section role="dialog" aria-modal="true" aria-labelledby="guide-title" className="guide-panel"><button autoFocus className="close-guide icon-button" onClick={onClose} aria-label="Close guide"><X/></button><div className="guide-heading"><span className="eyebrow">LESS GUESSWORK. MORE GAME DAY.</span><h2 id="guide-title">Know before<br/>you go.</h2><p>{item.event.name}</p><div className="guide-meta"><MapPin size={15}/>{item.event.venue}<span>·</span>{eventDate(item.event.start_time)}</div></div>
 <div className="guide-tabs" role="tablist">{['essentials','food & arrival','parking & comfort','sources'].map(t=><button role="tab" aria-selected={tab===t} key={t} onClick={()=>setTab(t)}>{t}</button>)}</div>
 <div className="guide-body"><div className="notice small"><Clock size={16}/><span>Stored policies · reviewed {item.guide.policy.last_verified || 'date unavailable'}. Recheck event-specific instructions before attending.</span></div>
 {item.guide.policy.conflicts.map(c=><div className="notice warning" key={c}><CircleAlert size={18}/><span>{c}</span></div>)}
 {tab==='essentials'&&<><div className="policy-grid">{fields.map(([key,label,Icon])=>{const p=item.guide.policy.fields[key];return <div className="policy-card" key={key}><Icon size={21}/><h3>{label}</h3><p>{p?.claim || 'Not verified in the current corpus. Check the official venue guide.'}</p>{p?<a href={sourceUrl(p.source_url)} target="_blank" rel="noreferrer">{p.freshness==='stale'?'Stale source':'Official source'} <ExternalLink size={12}/></a>:<span className="unverified">Information gap</span>}</div>;})}</div>{item.guide.policy.fields.clutch_dimensions&&<div className="notice small"><ShoppingBag size={18}/><span>{item.guide.policy.fields.clutch_dimensions.claim} See Sources for conflicting guidance.</span></div>}<div className="guide-tradeoffs"><h3>The tradeoffs, upfront.</h3>{item.tradeoffs.map(t=><p key={t}><ArrowRight size={15}/>{t}</p>)}</div></>}
 {tab==='food & arrival'&&<><h3 className="subheading">Something for your appetite.</h3>{item.guide.food.length?item.guide.food.map(f=><div className="food-option" key={f.evidence.id}><Utensils size={24}/><div><h3>{f.vendor}</h3>{f.location&&<small>{f.location}</small>}<p>{f.evidence.claim}</p><div className="fit-tags"><span>{f.vegetarian===true?'Vegetarian listed':'Vegetarian unverified'}</span>{f.vegan===true&&<span>Vegan listed</span>}</div><small>{f.allergen_information}</small><a href={sourceUrl(f.evidence.source_url)} target="_blank" rel="noreferrer">Check official menu <ArrowUpRight size={14}/></a></div></div>):<p className="notice">Food options have not been verified for this venue.</p>}<h3 className="subheading">Make arrival easy.</h3>{item.guide.arrival.length?item.guide.arrival.map(a=><p className="arrival-item" key={a}><Check size={17}/>{a}</p>):<p>Event-specific arrival guidance is unavailable. Check your ticket and the venue’s official instructions.</p>}<p className="fine-print">{item.distance_miles} miles is straight-line distance. This prototype does not estimate driving time or parking availability.</p></>}
 {tab==='parking & comfort'&&<PreparationDetails item={item}/>}
 {tab==='sources'&&<><h3 className="subheading">The evidence behind your outing.</h3><p className="fine-print">Official sources support venue and historical claims. The separate scenario fixture supports only illustrative dates, prices and editorial scoring inputs.</p>{item.citations.map(c=><a className="source-card" key={c.id} href={sourceUrl(c.source_url)} target="_blank" rel="noreferrer"><div><span>{c.authority.replaceAll('_',' ')} · {c.freshness}</span><h4>{c.source_title}</h4><p>{c.claim}</p><small>Retrieved {new Date(c.retrieved_at).toLocaleDateString('en-US')} · Source ID: {c.source_id}</small></div><ArrowUpRight size={18}/></a>)}</>}
 <section className="feedback"><h3>Does this feel like your kind of outing?</h3><div className="feedback-row"><button aria-pressed={feedback==='up'} aria-label="Thumbs up" onClick={()=>setFeedback('up')}><ThumbsUp size={18}/></button><button aria-pressed={feedback==='down'} aria-label="Thumbs down" onClick={()=>setFeedback('down')}><ThumbsDown size={18}/></button></div><label>Anything we should know?<input value={reason} maxLength={1000} onChange={e=>setReason(e.target.value)} placeholder="Optional reason"/></label><label>Report a correction<input value={correction} maxLength={1000} onChange={e=>setCorrection(e.target.value)} placeholder="Something in the guide looks incorrect…"/></label><div className="feedback-row"><button onClick={()=>send(true)}>I’d attend <Check size={15}/></button><button onClick={()=>send(false)}>Not this time</button></div><p role="status">{saved}</p></section>
 </div><footer className="guide-footer"><span><Ticket size={18}/>{item.event.data_mode==='illustrative'?'Illustrative fixture · check real listings':'Check availability on the official website'}</span><a className="button dark" href={sourceUrl(item.event.ticket_url)} target="_blank" rel="noreferrer">Official website <ArrowUpRight size={16}/></a></footer></section></div>;
}
