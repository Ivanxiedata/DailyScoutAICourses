"use client";

import { FormEvent, useMemo, useState } from "react";
import type { UIField, UISchema } from "@/lib/schema";
import { runPlugin } from "@/lib/api";

type DynamicFormProps = {
  schema: UISchema;
  onResult: (result: unknown) => void;
  onError: (error: string | null) => void;
};

function normalizeValue(field: UIField, value: string | boolean): unknown {
  if (field.type === "checkbox") return Boolean(value);
  if (field.type === "number") return Number(value);
  if (field.name === "key_points" && typeof value === "string") {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return value;
}

export function DynamicForm({ schema, onResult, onError }: DynamicFormProps) {
  const initialState = useMemo(() => {
    const state: Record<string, string | boolean> = {};
    schema.fields.forEach((field) => {
      if (typeof field.default !== "undefined") {
        state[field.name] = field.default as string | boolean;
      } else if (field.type === "checkbox") {
        state[field.name] = false;
      } else {
        state[field.name] = "";
      }
    });
    return state;
  }, [schema.fields]);

  const [formState, setFormState] = useState<Record<string, string | boolean>>(initialState);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    onError(null);
    setSubmitting(true);
    try {
      const payload: Record<string, unknown> = {};
      schema.fields.forEach((field) => {
        payload[field.name] = normalizeValue(field, formState[field.name]);
      });
      const result = await runPlugin(payload);
      onResult(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      onError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      {schema.fields.map((field) => (
        <div key={field.name} style={{ marginBottom: "1rem" }}>
          <label style={{ display: "block", marginBottom: ".4rem" }}>{field.label}</label>
          {field.type === "textarea" ? (
            <textarea
              required={field.required}
              value={String(formState[field.name] ?? "")}
              onChange={(event) =>
                setFormState((prev) => ({ ...prev, [field.name]: event.target.value }))
              }
              style={{ width: "100%", minHeight: "6rem" }}
            />
          ) : field.type === "select" ? (
            <select
              required={field.required}
              value={String(formState[field.name] ?? "")}
              onChange={(event) =>
                setFormState((prev) => ({ ...prev, [field.name]: event.target.value }))
              }
            >
              {(field.options ?? []).map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          ) : field.type === "checkbox" ? (
            <input
              type="checkbox"
              checked={Boolean(formState[field.name])}
              onChange={(event) =>
                setFormState((prev) => ({ ...prev, [field.name]: event.target.checked }))
              }
            />
          ) : (
            <input
              type={field.type}
              required={field.required}
              value={String(formState[field.name] ?? "")}
              onChange={(event) =>
                setFormState((prev) => ({ ...prev, [field.name]: event.target.value }))
              }
              style={{ width: "100%" }}
            />
          )}
        </div>
      ))}
      <button type="submit" disabled={submitting}>
        {submitting ? "Running..." : "Run Plugin"}
      </button>
    </form>
  );
}
