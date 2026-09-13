import { describe,it,expect } from 'vitest';
import { fitCopy } from './presentation';
import type { Recommendation,Results } from './types';

const event={event:{sport:'baseball',price_min:14,data_mode:'illustrative'},distance_miles:1.8,estimated_total:92,explanation:'A supplied explanation.',why_it_matters:['Supplied rivalry history.'],citations:[{category:'policy',claim:'Bag policy.'},{category:'context',claim:'Supplied rivalry history.'}]} as Recommendation;
const intent:Results['parsed_intent']={dietary:[],additional_constraints:[],location:'San Jose',radius_miles:25,budget:120,budget_type:'total',adults:2,children:2,atmosphere:'relaxed',sports:[]};
describe('recommendation fit copy',()=>{
 it('ties actual outing costs and distance to the requested limits',()=>{
  expect(fitCopy(event,intent).lead).toContain('$92 illustrative outing estimate for 4 people, within your $120 total budget');
  expect(fitCopy(event,intent).lead).toContain('within your 25-mile radius');
 });
 it('leads an unrestricted iconic request with supplied context rather than policy or cost',()=>{
  const copy=fitCopy(event,{...intent,atmosphere:'iconic',budget:null,radius_miles:null});
  expect(copy.lead).toBe('Supplied rivalry history.');
  expect(copy.supporting).toBe('');
 });
 it('respects per-ticket budget semantics and never claims an over-budget outing fits',()=>{
  expect(fitCopy(event,{...intent,budget:20,budget_type:'per_ticket'}).lead).toContain('$14 illustrative ticket price');
  expect(fitCopy(event,{...intent,budget:20}).lead).not.toContain('total budget');
 });
});
