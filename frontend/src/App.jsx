import { useState } from 'react'
import { useChat } from './useChat'
import AnswerCard from './components/AnswerCard'
import './App.css'

const SAMPLES = [
  'Which county has the most collisions?',
  'What percentage of collisions involved a parked vehicle?',
  'How many collisions happened each day of the week?',
  'Fatal collision rate by weather',
]

export default function App() {
  const { messages, loading, ask, cancel } = useChat()
  const [q, setQ] = useState('')

  const submit = (e) => {
    e.preventDefault()
    if (!q.trim()) return
    ask(q.trim())
    setQ('')
  }

  return (
    <div className="app">
      <header>
        <h1>🚗 SWITRS Collision Chatbot</h1>
        <p>California traffic collisions, 2001–2021. Ask anything.</p>
      </header>

      <div className="samples">
        {SAMPLES.map((s) => (
          <button key={s} onClick={() => ask(s)} disabled={loading}>{s}</button>
        ))}
      </div>

      <div className="messages">
        {messages.map((m) => <AnswerCard key={m.id} msg={m} />)}
      </div>

      <form className="composer" onSubmit={submit}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Ask about California collisions…"
        />
        <button type="submit" disabled={loading}>Ask</button>
        {loading && <button type="button" onClick={cancel}>Stop</button>}
      </form>
    </div>
  )
}
