const { useState, useEffect } = React;

function Scanner() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  const startScan = async (e) => {
    e.preventDefault();
    if (!url) return;
    
    setLoading(true);
    setError(null);
    setReport(null);
    setStatusText('Starting scan...');

    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      
      if (!res.ok) throw new Error('Failed to start scan (ensure you are logged in)');
      
      const data = await res.json();
      const taskId = data.task_id;
      setStatusText('Scan in progress...');
      
      pollStatus(taskId);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const pollStatus = (taskId) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/scan/${taskId}/status`);
        const data = await res.json();
        
        if (data.state === 'SUCCESS') {
          clearInterval(interval);
          setReport(data.result);
          setLoading(false);
        } else if (data.state === 'FAILURE') {
          clearInterval(interval);
          setError('Scan failed.');
          setLoading(false);
        } else {
          setStatusText(`Status: ${data.state}...`);
        }
      } catch (err) {
        clearInterval(interval);
        setError('Error polling status');
        setLoading(false);
      }
    }, 2000);
  };

  return (
    <div className="container">
      <div className="header">
        <h1>VulnScan Lite</h1>
        <div style={{color: 'var(--text-muted)'}}>Only scan websites you own. Passive analysis only.</div>
      </div>

      <div className="card">
        <form onSubmit={startScan} style={{display: 'flex', gap: '1rem'}}>
          <input 
            type="text" 
            placeholder="https://example.com" 
            value={url} 
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
            style={{marginBottom: 0}}
          />
          <button type="submit" disabled={loading || !url}>
            {loading ? 'Scanning...' : 'Start Scan'}
          </button>
        </form>
        
        {loading && <div style={{marginTop: '1rem', color: 'var(--primary)'}}>{statusText}</div>}
        {error && <div style={{marginTop: '1rem', color: 'var(--danger)'}}>{error}</div>}
      </div>

      {report && <ReportCard report={report} />}
    </div>
  );
}

function ReportCard({ report }) {
  const getGradeClass = (grade) => {
    return `score-${grade}`;
  };

  return (
    <div className="card">
      <div className="header">
        <h2>Security Health Report</h2>
        <button onClick={() => window.print()} style={{padding: '0.5rem 1rem', fontSize: '0.9rem'}}>Export PDF</button>
      </div>

      <div className="grid">
        <div style={{textAlign: 'center'}}>
          <div className={`score-circle ${getGradeClass(report.grade)}`}>
            <h2>{report.grade}</h2>
            <span>{report.score}/100</span>
          </div>
          <div style={{marginTop: '1rem', color: 'var(--text-muted)', wordBreak: 'break-all'}}>
            Scanned URL: {report.url}
          </div>
        </div>

        <div>
          <h3>Issues Found</h3>
          {report.issues && report.issues.length > 0 ? (
            <div style={{marginTop: '1rem'}}>
              {report.issues.map((issue, idx) => {
                const remediation = report.remediation?.find(r => r.issue === issue);
                return (
                  <div key={idx} className="list-item">
                    <span className="icon icon-fail">✗</span>
                    <div>
                      <div style={{fontWeight: 500}}>{issue}</div>
                      {remediation && (
                        <div className="remediation-box">
                          <strong>How to Fix:</strong> {remediation.tip}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{marginTop: '1rem', color: 'var(--success)'}}>No critical issues found!</div>
          )}

          <h3 style={{marginTop: '2rem'}}>Passed Checks</h3>
          {report.passed_checks && report.passed_checks.length > 0 ? (
            <div style={{marginTop: '1rem'}}>
              {report.passed_checks.map((check, idx) => (
                <div key={idx} className="list-item">
                  <span className="icon icon-pass">✓</span>
                  <div>{check}</div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{marginTop: '1rem', color: 'var(--text-muted)'}}>No checks passed.</div>
          )}
        </div>
      </div>
    </div>
  );
}

ReactDOM.render(<Scanner />, document.getElementById('root'));
