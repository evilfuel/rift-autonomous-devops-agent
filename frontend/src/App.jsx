import { useState } from "react";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [teamName, setTeamName] = useState("");
  const [leaderName, setLeaderName] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    const response = await fetch("http://127.0.0.1:8000/run-agent", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        repo_url: repoUrl,
        team_name: teamName,
        leader_name: leaderName,
      }),
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>Autonomous DevOps Agent</h1>

      <input
        placeholder="GitHub Repo URL"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
      />
      <br /><br />

      <input
        placeholder="Team Name"
        value={teamName}
        onChange={(e) => setTeamName(e.target.value)}
      />
      <br /><br />

      <input
        placeholder="Leader Name"
        value={leaderName}
        onChange={(e) => setLeaderName(e.target.value)}
      />
      <br /><br />

      <button onClick={handleSubmit}>Run Agent</button>

      {result && (
        <pre style={{ marginTop: "30px" }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default App;
