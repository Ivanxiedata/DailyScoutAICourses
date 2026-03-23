const backendBaseUrl =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

export async function runPlugin(inputs: Record<string, unknown>) {
  const response = await fetch(`${backendBaseUrl}/api/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ inputs })
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Backend error (${response.status}): ${body}`);
  }

  return response.json();
}
