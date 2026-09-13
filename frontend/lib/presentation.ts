import type { Recommendation, Results } from './types';
import { money } from './api';

/** Summarize only enforced constraints and supplied context, without new model claims. */
export function fitCopy(item:Recommendation, intent:Results['parsed_intent']) {
 const context = item.citations.find(c=>c.category==='context' && item.why_it_matters.includes(c.claim))
  || item.citations.find(c=>c.category==='context');
 const facts:string[]=[];
 if(intent.radius_miles!==null && item.distance_miles!==null && item.distance_miles<=intent.radius_miles)
  facts.push(`${item.distance_miles} straight-line miles from ${intent.location}, within your ${intent.radius_miles}-mile radius.`);
 if(intent.budget!==null) {
  const illustrative=item.event.data_mode==='illustrative'?'illustrative ':'';
  if(intent.budget_type==='total' && item.estimated_total!==null && item.estimated_total<=intent.budget)
   facts.push(`${money(item.estimated_total)} ${illustrative}outing estimate for ${intent.adults+intent.children} people, within your ${money(intent.budget)} total budget.`);
  if(intent.budget_type==='per_ticket' && item.event.price_min!==null && item.event.price_min<=intent.budget)
   facts.push(`${money(item.event.price_min)} ${illustrative}ticket price, within your ${money(intent.budget)} per-ticket limit.`);
 }
 if(intent.sports?.includes(item.event.sport))facts.push(`Matches your ${item.event.sport} preference.`);
 const contextFirst=['iconic','rivalry','electric'].includes(intent.atmosphere) || !facts.length;
 return {
  lead:contextFirst && context ? context.claim : facts.join(' ') || item.explanation,
  supporting:contextFirst && context ? facts.join(' ') : context?.claim,
 };
}
