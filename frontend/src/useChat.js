import { useState, useCallback, useRef } from 'react'

// Parses an SSE stream from POST /chat/stream into incremental state updates.
export function useChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const abortRef = useRef(null)
  const answerRef = useRef({}) // id -> accumulated answer text

  const ask = useCallback(async (question) => {
    setLoading(true)
    const id = Date.now()
    answerRef.current[id] = ''
    setMessages((m) => [
      ...m,
      {
        id, question, sql: '', restatement: '', columns: [], rows: [],
        chartSpec: { type: 'none' }, answer: '', error: null, stage: 'thinking',
      },
    ])
    const update = (patch) =>
      setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, ...patch } : msg)))

    const controller = new AbortController()
    abortRef.current = controller
    try {
      const resp = await fetch('/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        signal: controller.signal,
      })
      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buf = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })
        const parts = buf.split('\n\n')
        buf = parts.pop()
        for (const part of parts) {
          const ev = part.match(/event: (.*)/)?.[1]
          const data = JSON.parse(part.match(/data: ([\s\S]*)/)?.[1] || '{}')
          if (ev === 'status') update({ stage: data.stage })
          else if (ev === 'sql') update({ sql: data.sql, restatement: data.restatement })
          else if (ev === 'rows')
            update({
              columns: data.columns, rows: data.rows,
              chartSpec: data.chart_spec, stage: 'answering',
            })
          else if (ev === 'answer') {
            answerRef.current[id] += data.token
            update({ answer: answerRef.current[id] })
          } else if (ev === 'error') update({ error: data.message, stage: 'done' })
          else if (ev === 'done') update({ stage: 'done' })
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') update({ error: String(e), stage: 'done' })
    } finally {
      setLoading(false)
    }
  }, [])

  const cancel = useCallback(() => abortRef.current?.abort(), [])
  return { messages, loading, ask, cancel }
}
