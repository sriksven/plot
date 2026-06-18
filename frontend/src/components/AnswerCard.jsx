import { useState } from 'react'
import Chart from './Chart'

export default function AnswerCard({ msg }) {
  const [showSql, setShowSql] = useState(false)
  return (
    <div className="card">
      <div className="question">{msg.question}</div>

      {msg.stage === 'thinking' && <div className="skeleton">Generating SQL…</div>}

      {msg.sql && (
        <div className="sql-block">
          <button onClick={() => setShowSql((s) => !s)}>
            {showSql ? 'Hide' : 'Show'} SQL (proof)
          </button>
          {showSql && <pre>{msg.sql}</pre>}
        </div>
      )}

      {msg.error && <div className="error">⚠ {msg.error}</div>}

      {msg.stage === 'querying' && <div className="skeleton">Running query…</div>}

      <Chart spec={msg.chartSpec} />

      {msg.rows?.length > 0 && (
        <div className="table-wrap">
          <table className="result">
            <thead>
              <tr>{msg.columns.map((c) => <th key={c}>{c}</th>)}</tr>
            </thead>
            <tbody>
              {msg.rows.slice(0, 50).map((r, i) => (
                <tr key={i}>{r.map((v, j) => <td key={j}>{String(v)}</td>)}</tr>
              ))}
            </tbody>
          </table>
          {msg.rows.length > 50 && (
            <div className="more">…showing first 50 of {msg.rows.length} rows</div>
          )}
        </div>
      )}

      {msg.answer && <div className="answer">{msg.answer}</div>}
    </div>
  )
}
