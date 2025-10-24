import React from 'react'


type Diff = {
  services_added: { port: number; protocol: string }[]
  services_removed: { port: number; protocol: string }[]
  services_modified: { port: number; protocol: string; changes: Record<string, any> }[]
}


export default function DiffView({ diff }: { diff: Diff | null }) {
  if (!diff) return null
  return (
    <div className="card">
      <h3>Diff Result</h3>
      <div className="row">
        <div>
          <h4>Added Services</h4>
          <ul>
            {diff.services_added.length === 0 && <li>None</li>}
            {diff.services_added.map((s, i) => <li key={i}>{s.protocol} {s.port}</li>)}
          </ul>
        </div>
      <div>
        <h4>Removed Services</h4>
        <ul>
          {diff.services_removed.length === 0 && <li>None</li>}
          {diff.services_removed.map((s, i) => <li key={i}>{s.protocol} {s.port}</li>)}
        </ul>
      </div>
      </div>
        <h4>Changed Services</h4>
        {diff.services_modified.length === 0 && <div>None</div>}
        {diff.services_modified.map((c, i) => (
        <details key={i}>
          <summary>{c.protocol} {c.port}</summary>
          <pre>{JSON.stringify(c.changes, null, 2)}</pre>
        </details>
      ))}
    </div>
  )
}