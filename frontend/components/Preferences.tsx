'use client';
import { SlidersHorizontal, ChevronDown, ArrowUpRight } from 'lucide-react';
import type { Filters } from '@/lib/types';

type Props = {
 filters: Filters; expanded: boolean; loading: boolean; mode: 'auto'|'agent'|'fallback';
 onExpand: () => void; onSearch: () => void; canSearch: boolean;
 onMode: (mode: Props['mode']) => void;
 update: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
};

export function Preferences({ filters:f, expanded, loading, mode, onExpand, onSearch, canSearch, onMode, update }: Props) {
 return <aside className={`preferences ${expanded?'preferences-open':''}`} aria-label="Your game plan" id="preferences">
  <div className="preferences-heading"><div><span className="eyebrow">MAKE IT YOUR DAY</span><h2>Your game plan</h2></div><SlidersHorizontal size={20}/></div>
  <button className="preferences-toggle" onClick={onExpand} aria-expanded={expanded} aria-controls="preferences-body">Your preferences <ChevronDown size={17}/></button>
  <div id="preferences-body" className="preferences-body">
   <p className="preference-hint">Start with your words. Fine-tune the details here.</p>
   <fieldset disabled={loading} className="preferences-fields"><legend className="sr-only">Outing preferences</legend>
    <div className="filter-grid">
     <label className="span-two">Starting from<input aria-label="Location or supported ZIP" value={f.location} onChange={e=>update('location',e.target.value)} maxLength={120}/></label>
     <label>Budget ($)<input type="number" min={0} placeholder="No limit" value={f.budget??''} onChange={e=>update('budget',e.target.value===''?null:Number(e.target.value))}/></label>
     <label>Radius (miles)<input type="number" min={1} max={500} placeholder="No limit" value={f.radius_miles??''} onChange={e=>update('radius_miles',e.target.value===''?null:Number(e.target.value))}/></label>
     <label className="span-two">Budget covers<select value={f.budget_type} onChange={e=>update('budget_type',e.target.value as Filters['budget_type'])}><option value="total">Total outing</option><option value="per_ticket">Per ticket</option></select></label>
     <label>Adults<input type="number" min={1} max={20} value={f.adults} onChange={e=>update('adults',Number(e.target.value))}/></label>
     <label>Children<input type="number" min={0} max={20} value={f.children} onChange={e=>update('children',Number(e.target.value))}/></label>
     <label className="span-two">Atmosphere<select value={f.atmosphere} onChange={e=>update('atmosphere',e.target.value)}>{['any','relaxed','electric','iconic','rivalry'].map(v=><option key={v}>{v}</option>)}</select></label>
     <label className="span-two">Dietary preference<select value={f.dietary[0]||''} onChange={e=>update('dietary',e.target.value?[e.target.value]:[])}><option value="">No preference</option><option>vegetarian</option><option>vegan</option><option>gluten-free</option></select></label>
    </div>
    <details className="more-preferences"><summary>Dates, sports & more <ChevronDown size={15}/></summary><div className="filter-grid">
     <label>From<input type="date" value={f.date_from||''} onChange={e=>update('date_from',e.target.value||null)}/></label>
     <label>Through<input type="date" value={f.date_to||''} onChange={e=>update('date_to',e.target.value||null)}/></label>
     <label className="span-two">Sport<select value={f.sports[0]||''} onChange={e=>update('sports',e.target.value?[e.target.value]:[])}><option value="">Open to any sport</option>{['baseball','football','volleyball','soccer'].map(v=><option key={v}>{v}</option>)}</select></label>
     <label className="span-two">Team<input placeholder="Any team" value={f.teams[0]||''} onChange={e=>update('teams',e.target.value?[e.target.value]:[])}/></label>
     <label className="span-two">Accessibility<select value={f.accessibility[0]||''} onChange={e=>update('accessibility',e.target.value?[e.target.value]:[])}><option value="">None specified</option><option value="wheelchair">Wheelchair seating required</option><option value="sensory room">Sensory room required</option></select></label>
    </div><div className="checkboxes">{[['family_friendly','Family-friendly'],['local_openness','Include local & college events'],['dietary_required','Only verified dietary matches'],['first_time','First-time attendee']].map(([key,label])=><label key={key}><input type="checkbox" checked={Boolean(f[key as keyof Filters])} onChange={e=>update(key as keyof Filters,e.target.checked)}/>{label}</label>)}</div>
    <div className="filter-grid"><label className="span-two">Concierge mode<select value={mode} onChange={e=>onMode(e.target.value as Props['mode'])}><option value="auto">Local agent · automatic fallback</option><option value="agent">Request local agent</option><option value="fallback">Non-agent fallback</option></select></label></div></details>
    <button className="button dark full sidebar-search" onClick={onSearch} disabled={!canSearch}>{loading?'Investigating…':'Find my pick'}<ArrowUpRight size={18}/></button>
   </fieldset>
   <p className="fine-print">Edited fields override your words. Other preferences are inferred from your request. Outing estimates include illustrative extras; actual costs may vary.</p>
  </div>
 </aside>;
}
