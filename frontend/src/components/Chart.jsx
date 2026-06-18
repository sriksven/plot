import Plot from 'react-plotly.js'
import { memo } from 'react'

function ChartImpl({ spec }) {
  if (!spec || spec.type === 'none') return null
  const trace =
    spec.type === 'pie'
      ? [{ type: 'pie', labels: spec.x, values: spec.y }]
      : [{ type: spec.type, x: spec.x, y: spec.y, marker: { color: '#8ab4f8' } }]
  return (
    <Plot
      data={trace}
      layout={{
        autosize: true,
        height: 320,
        margin: { t: 20, r: 10, b: 60, l: 60 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e8eaed' },
        xaxis: { title: spec.x_label },
        yaxis: { title: spec.y_label },
      }}
      style={{ width: '100%' }}
      useResizeHandler
      config={{ displayModeBar: false, responsive: true }}
    />
  )
}
export default memo(ChartImpl)
