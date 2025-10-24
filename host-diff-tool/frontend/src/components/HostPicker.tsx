import React, { useEffect, useState } from 'react'
import { getHosts } from '../api'


export default function HostPicker({ value, onChange }: { value: string | null; onChange: (v: string | null) => void }) {
  const [hosts, setHosts] = useState<string[]>([])


  useEffect(() => {
    getHosts().then(h => setHosts(h.hosts)).catch(console.error)
  }, [])


  return (
    <div className="card">
      <h3>Pick Host</h3>
      <select value={value ?? ''} onChange={e => onChange(e.target.value || null)}>
        <option value="">— Select —</option>
        {hosts.map(h => (
          <option key={h} value={h}>{h}</option>
        ))}
      </select>
    </div>
  )
}