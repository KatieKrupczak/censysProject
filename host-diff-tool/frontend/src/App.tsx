import React, { useState } from 'react'
import UploadForm from './components/UploadForm'
import HostPicker from './components/HostPicker'
import SnapshotPicker from './components/SnapshotPicker'
import DiffView from './components/DiffView'
import { getDiff } from './api'


export default function App(){
  const [selectedHost, setSelectedHost] = useState<string | null>(null)
  const [a, setA] = useState<string | null>(null)
  const [b, setB] = useState<string | null>(null)
  const [diff, setDiff] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)


  async function runDiff(){
    setError(null)
    setDiff(null)
    if (!selectedHost || !a || !b) { setError('Pick host and two snapshots.'); return }
    try {
      const res = await getDiff(selectedHost, a, b)
      setDiff(res.diff)
    } catch (e:any) {
      setError(e.message)
    }
  }


  return (
    <div className="container">
      <h1>Host Diff Tool</h1>
      <p className="muted">Upload Censys host snapshots, select two versions, and view what changed.</p>

      <UploadForm onUploaded={() => { /* no-op; HostPicker pulls fresh list on mount */ }} />
      <HostPicker value={selectedHost} onChange={(v)=>{ setSelectedHost(v); setA(null); setB(null); setDiff(null)}} />
      <SnapshotPicker ip={selectedHost} a={a} b={b} onChange={(na, nb)=>{ setA(na); setB(nb) }} />
      <div className="card">
        <button onClick={runDiff} disabled={!selectedHost || !a || !b}>Compare</button>
        {error && <div className="error">{error}</div>}
      </div>
      <DiffView diff={diff} />
    </div>
  )
}