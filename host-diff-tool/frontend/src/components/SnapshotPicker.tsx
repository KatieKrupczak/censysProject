import React, { useEffect, useState } from 'react'
import { getSnapshots } from '../api'


export default function SnapshotPicker({ ip, a, b, onChange }:{ ip: string | null, a: string | null, b: string | null, onChange: (a: string | null, b: string | null) => void }){
  const [timestamps, setTimestamps] = useState<string[]>([])


  useEffect(() => {
    if (!ip) { setTimestamps([]); return }
    getSnapshots(ip).then(r => setTimestamps(r.timestamps)).catch(console.error)
  }, [ip])


  return (
    <div className="card">
      <h3>Pick Two Snapshots</h3>
      <div className="row">
        <select value={a ?? ''} onChange={e => onChange(e.target.value || null, b)} disabled={!ip}>
          <option value="">— Snapshot A —</option>
          {timestamps.map(ts => <option key={ts} value={ts}>{ts}</option>)}
        </select>
        <select value={b ?? ''} onChange={e => onChange(a, e.target.value || null)} disabled={!ip}>
          <option value="">— Snapshot B —</option>
          {timestamps.map(ts => <option key={ts} value={ts}>{ts}</option>)}
        </select>
      </div>
    </div>
  )
}