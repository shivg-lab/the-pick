export function FieldArt({ sport = 'baseball', variant = 'orange', hero = false }: { sport?: string; variant?: string; hero?: boolean }) {
  const colors: Record<string, string[]> = { orange: ['#ed652c', '#f6aa73', '#293c31'], red: ['#b84134', '#e79775', '#31453d'], blue: ['#2c5260', '#91b3ad', '#ddd3a9'], navy: ['#273a48', '#8ba29b', '#dbbb8e'] };
  const c = colors[variant] || colors.orange;
  return <svg className={`field-art ${hero ? 'hero-art' : ''}`} viewBox="0 0 620 440" preserveAspectRatio="xMidYMid slice" role="img" aria-label={`Original illustration of a ${sport} stadium`}>
    <defs><pattern id={`crowd-${variant}-${sport}-${hero}`} width="15" height="15" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="1.6" fill={c[1]} /></pattern></defs>
    <path fill={c[0]} d="M0 0h620v440H0z" />
    <circle cx="490" cy="90" r="49" fill="#f8ddb0" />
    <g fill="none" stroke={c[1]} strokeWidth="1" opacity=".65"><path d="M-30 360 620 23M-30 410 620 73M0 440 620 123M60 440 620 173M110 440 620 223" /></g>
    <g transform="translate(308 260) rotate(-24)">
      <ellipse rx="264" ry="131" fill="#f6dbb1" />
      <ellipse cy="-12" rx="264" ry="131" fill="#27332e" />
      <ellipse cy="-12" rx="253" ry="120" fill={`url(#crowd-${variant}-${sport}-${hero})`} />
      <g stroke="#f5caa0" fill="none" opacity=".7"><ellipse cy="-12" rx="240" ry="108"/><ellipse cy="-12" rx="217" ry="95"/><ellipse cy="-12" rx="193" ry="81"/></g>
      <ellipse cy="-12" rx="173" ry="70" fill={c[2]} />
      {sport === 'baseball' ? <g transform="translate(0 -8) scale(1 .52)"><path d="M-115-78Q0-160 115-78L0 100Z" fill="#68866a"/><path d="m0 100-73-73 73-73 73 73Z" fill="#d2a577"/><path d="m0 66-41-40 41-40 41 40Z" fill="#7f956c"/><path d="M0 100-116-78M0 100 116-78" stroke="#fff3d6" strokeWidth="3"/><path d="m0 100-5-7 5-5 5 5Z" fill="#fff3d6"/><circle cy="26" r="6" fill="#d2a577"/></g> : <g transform="translate(0 -12)"><path d="M-132-49H132V49H-132Z" fill="#698565" stroke="#eee5c7" strokeWidth="2"/>{[-100,-65,-32,0,32,65,100].map(x => <path key={x} d={`M${x}-49V49`} stroke="#eee5c7" opacity=".55" />)}<ellipse rx="22" ry="18" fill="none" stroke="#eee5c7"/></g>}
      <path d="M-188-99V-157M185-99V-157" stroke="#24342e" strokeWidth="5"/><path d="M-218-157H-158M155-157H215" stroke="#f8edcf" strokeWidth="11"/>
    </g>
    <g fill="#26382d"><path d="m60 65 8-5 8 5-8-2Z"/><path d="m88 51 8-5 8 5-8-2Z"/><path d="m470 168 8-5 8 5-8-2Z"/></g>
    <text x="29" y="411" fill="#fff0d8" fontSize="10" fontFamily="monospace" letterSpacing="3">BAY AREA / LIVE & IN PERSON</text>
  </svg>;
}
