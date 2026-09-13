import { ArrowUpRight, CarFront, Armchair, Shirt, ExternalLink } from 'lucide-react';
import type { Evidence, Recommendation } from '@/lib/types';
import { WeatherSummary } from './Weather';
import { sourceUrl } from '@/lib/api';

function Source({ evidence }: { evidence: Evidence }) {
 return <a href={sourceUrl(evidence.source_url)} target="_blank" rel="noreferrer">{evidence.freshness==='stale'?'Older guidance · recheck':'Official source'} <ExternalLink size={12}/><small>Reviewed {new Date(evidence.retrieved_at).toLocaleDateString('en-US')}</small></a>;
}

export function PreparationPreview({ item, onOpen }: { item: Recommendation; onOpen: () => void }) {
 const guide=item.guide;
 const facts=[
  {label:'Parking',Icon:CarFront,text:guide.parking?.[0]?.claim,older:guide.parking?.[0]?.freshness==='stale'},
  {label:'Seating convenience',Icon:Armchair,text:guide.seating?.[0]?.claim},
  {label:'What to wear',Icon:Shirt,text:guide.attire_tips?.[0],suggestion:true},
 ];
 return <div className="preparation-preview"><div className="preparation-heading"><h5>Make yourself comfortable.</h5><button className="text-button" onClick={onOpen}>Parking & comfort <ArrowUpRight size={16}/></button></div><div className="preparation-grid">{facts.map(({label,Icon,text,older,suggestion})=><div key={label}><Icon size={18}/><h5>{label}</h5><p>{text||'Details not verified. Open the guide for what to check.'}</p><small>{suggestion?(guide.weather?.status==='available'?'Weather-informed suggestion':'Comfort suggestion'):older?'Older guidance · confirm this season':text?'Stored venue guidance':'Check with the venue'}</small></div>)}</div></div>;
}

export function PreparationDetails({ item }: { item: Recommendation }) {
 const guide=item.guide;
 return <section className="preparation-details" aria-label="Parking and comfort guidance">
  <div className="preparation-section"><h3><CarFront size={22}/> A smoother arrival.</h3><p className="fine-print">Parking locations and booking guidance. Current prices, lot availability and walking times are not verified.</p>{guide.parking?.length?guide.parking.map(e=><article className="preparation-source" key={e.id}><p>{e.claim}</p><Source evidence={e}/></article>):<p className="notice">Parking details are not verified for this venue. Check its official website before driving.</p>}</div>
  <div className="preparation-section"><h3><Armchair size={22}/> Find a comfortable seat.</h3>{guide.seating?.length?guide.seating.map(e=><article className="preparation-source" key={e.id}><p>{e.claim}</p><Source evidence={e}/></article>):<p className="notice">Seating details are not verified for this venue. Ask the ticket office about suitable sections.</p>}{guide.seating_tip&&<div className="comfort-tip"><span>SEAT-CHOOSING TIP</span><p>{guide.seating_tip}</p></div>}<p className="fine-print">Seat availability, views and shade are not guaranteed. Arrange any accessible seating before buying tickets.</p></div>
  <div className="preparation-section attire-section"><h3><Shirt size={22}/> What to wear.</h3><WeatherSummary weather={guide.weather} illustrative={item.event.data_mode==='illustrative'}/><span className="suggestion-label">{guide.weather?.status==='available'?'Weather-informed comfort suggestions · venue rules below':'General comfort suggestions · forecast unavailable'}</span>{guide.attire_tips?.length?<ul>{guide.attire_tips.map(t=><li key={t}>{t}</li>)}</ul>:<p>Run a new search for the latest comfort suggestions.</p>}<h4 className="attire-rules-heading">Venue clothing & umbrella rules</h4>{guide.attire_rules?.length?guide.attire_rules.map(e=><article className="preparation-source" key={e.id}><p>{e.claim}</p><Source evidence={e}/></article>):<p className="fine-print">Specific clothing and umbrella requirements are not verified for this venue. Check its official event guide.</p>}</div>
 </section>;
}
