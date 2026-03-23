"use client";

import { useState } from "react";
import { DynamicForm } from "@/components/DynamicForm";
import { ResultPanel } from "@/components/ResultPanel";
import { schema } from "@/lib/schema";

export default function HomePage() {
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <main>
      <h1>{schema.title}</h1>
      <p>{schema.description}</p>
      <DynamicForm schema={schema} onResult={setResult} onError={setError} />
      <hr style={{ margin: "1.5rem 0" }} />
      <ResultPanel result={result} error={error} />
    </main>
  );
}
