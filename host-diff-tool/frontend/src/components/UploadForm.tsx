import React, { useState } from 'react'
import { uploadSnapshot } from '../api'


export default function UploadForm({ onUploaded }: { onUploaded: () => void }) {
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)


  const onChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    
    if (!file) return
    
    setBusy(true)
    setMsg(null)
    
    try {
      const res = await uploadSnapshot(file)
      setMsg(`Uploaded ${res.ip} @ ${res.timestamp}`)
      onUploaded()
    } catch (e: any) {
      setMsg(`Error: ${e.message}`)
    } finally {
      setBusy(false)
      e.target.value = ''
    }
  }


  return (
    <div className="card">
      <h3>Upload Snapshot</h3>
      <input type="file" accept="application/json,.json" onChange={onChange} disabled={busy} />
      {msg && <div className="muted">{msg}</div>}
    </div>
  )
}