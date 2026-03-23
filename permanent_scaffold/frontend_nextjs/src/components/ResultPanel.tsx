type ResultPanelProps = {
  result: unknown;
  error: string | null;
};

export function ResultPanel({ result, error }: ResultPanelProps) {
  return (
    <section>
      <h2>Result</h2>
      {error ? (
        <pre style={{ color: "#b91c1c", whiteSpace: "pre-wrap" }}>{error}</pre>
      ) : (
        <pre style={{ whiteSpace: "pre-wrap" }}>
          {result ? JSON.stringify(result, null, 2) : "No result yet."}
        </pre>
      )}
    </section>
  );
}
