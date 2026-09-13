import { CloudSun, ExternalLink } from 'lucide-react';
import type { EventWeather } from '@/lib/types';
import { sourceUrl } from '@/lib/api';

function range(low: number | null, high: number | null) {
 return low===null||high===null?'Unavailable':`${Math.round(low)}–${Math.round(high)}°F`;
}
function time(value: string) {
 return new Date(value).toLocaleString('en-US',{timeZone:'America/Los_Angeles',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
}
export function WeatherSummary({ weather, illustrative }: { weather?: EventWeather; illustrative: boolean }) {
 const available=weather?.status==='available';
 const old=weather?.retrieved_at && Date.now()-new Date(weather.retrieved_at).getTime()>30*60*1000;
 return <div className="weather-summary" aria-label="Event-time weather"><h4><CloudSun size={21}/> Weather for your outing</h4>
  {available?<><div className="weather-stats"><div><small>Temperature</small><strong>{range(weather.temperature_min_f,weather.temperature_max_f)}</strong></div><div><small>Feels like</small><strong>{range(weather.feels_like_min_f,weather.feels_like_max_f)}</strong></div><div><small>Highest hourly rain chance</small><strong>{weather.rain_probability_max===null?'Unavailable':`${Math.round(weather.rain_probability_max)}%`}</strong></div><div><small>Wind up to</small><strong>{weather.wind_max_mph===null?'Unavailable':`${Math.round(weather.wind_max_mph)} mph`}</strong></div></div>
   {weather.window_start&&weather.window_end&&<p>{time(weather.window_start)} – {time(weather.window_end)} PT</p>}
   <p>{weather.message}</p><p>{old?'Saved forecast · run a new pick to refresh.':'Forecasts can change; recheck before leaving.'} {weather.retrieved_at&&`Retrieved ${time(weather.retrieved_at)} PT.`}</p>
   <a href={sourceUrl(weather.source_url)} target="_blank" rel="noreferrer">Weather data by Open-Meteo <ExternalLink size={12}/></a><small className="weather-credit">Hourly data summarized for this planning window.</small>
  </>:<p>{weather?.message||'Run a new search to check the event-time forecast.'}</p>}
  {illustrative&&<p className="weather-demo">{available?'Real forecast for an illustrative event date; this does not confirm the fixture.':'The event date is illustrative.'}</p>}
 </div>;
}
