"use client";

import { FormEvent, useMemo, useState } from "react";
import type { UIField, UISchema } from "@/lib/schema";
import { runPlugin } from "@/lib/api";

type DynamicFormProps = {
  schema: UISchema;
  onResult: (result: unknown) => void;
  onError: (error: string | null) => void;
};

/** Serialized file for JSON POST to FastAPI */
export type UploadedFilePayload = {
  filename: string;
  mimeType: string;
  encoding: "utf-8" | "base64";
  content: string;
};

type FormValue = string | boolean | File | null;

/** Narrow plugin form state to `File | null` (indexed `FormValue` often won't narrow with a ternary). */
function toFileOrNull(value: FormValue): File | null {
  return value instanceof File ? value : null;
}

/** Maps schema type strings to a canonical widget key */
const CANONICAL_WIDGET: Record<string, string> = {
  text: "text",
  text_input: "text",
  number: "number",
  select: "select",
  textarea: "textarea",
  checkbox: "checkbox",
  file_upload: "file_upload"
};

function normalizeWidgetType(field: UIField): string {
  return CANONICAL_WIDGET[field.type] ?? "text";
}

async function fileToPayload(file: File): Promise<UploadedFilePayload> {
  const isText =
    file.type.startsWith("text/") ||
    file.type === "application/json" ||
    file.name.toLowerCase().endsWith(".md") ||
    file.name.toLowerCase().endsWith(".txt") ||
    file.name.toLowerCase().endsWith(".csv");

  if (isText) {
    const text = await file.text();
    return {
      filename: file.name,
      mimeType: file.type || "text/plain",
      encoding: "utf-8",
      content: text
    };
  }

  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  const base64 = btoa(binary);

  return {
    filename: file.name,
    mimeType: file.type || "application/octet-stream",
    encoding: "base64",
    content: base64
  };
}

function normalizeValue(field: UIField, value: FormValue): unknown {
  const widget = normalizeWidgetType(field);

  if (widget === "checkbox") return Boolean(value);
  if (widget === "number") return Number(value);
  if (widget === "file_upload") {
    if (value instanceof File) {
      return value;
    }
    return null;
  }
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
    const state: Record<string, FormValue> = {};
    schema.fields.forEach((field) => {
      const widget = normalizeWidgetType(field);
      if (widget === "file_upload") {
        state[field.name] = null;
      } else if (typeof field.default !== "undefined") {
        state[field.name] = field.default as string | boolean;
      } else if (widget === "checkbox") {
        state[field.name] = false;
      } else {
        state[field.name] = "";
      }
    });
    return state;
  }, [schema.fields]);

  const [formState, setFormState] = useState<Record<string, FormValue>>(initialState);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    onError(null);
    setSubmitting(true);
    try {
      const payload: Record<string, unknown> = {};
      for (const field of schema.fields) {
        const widget = normalizeWidgetType(field);
        const raw = formState[field.name];
        if (widget === "file_upload") {
          if (raw instanceof File) {
            payload[field.name] = await fileToPayload(raw);
          } else if (field.required) {
            throw new Error(`Missing required file: ${field.label}`);
          }
        } else {
          payload[field.name] = normalizeValue(field, raw);
        }
      }
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
      {schema.fields.map((field) => {
        const widget = normalizeWidgetType(field);
        const fileForDropzone = toFileOrNull(formState[field.name]);

        return (
          <div key={field.name} style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: ".4rem" }}>{field.label}</label>
            {widget === "textarea" ? (
              <textarea
                required={field.required}
                value={String(formState[field.name] ?? "")}
                onChange={(event) =>
                  setFormState((prev) => ({ ...prev, [field.name]: event.target.value }))
                }
                style={{ width: "100%", minHeight: "6rem" }}
              />
            ) : widget === "select" ? (
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
            ) : widget === "checkbox" ? (
              <input
                type="checkbox"
                checked={Boolean(formState[field.name])}
                onChange={(event) =>
                  setFormState((prev) => ({ ...prev, [field.name]: event.target.checked }))
                }
              />
            ) : widget === "file_upload" ? (
              <FileDropzone
                required={field.required}
                file={fileForDropzone}
                onFile={(file) => setFormState((prev) => ({ ...prev, [field.name]: file }))}
              />
            ) : (
              <input
                type={widget === "number" ? "number" : "text"}
                required={field.required}
                value={String(formState[field.name] ?? "")}
                onChange={(event) =>
                  setFormState((prev) => ({ ...prev, [field.name]: event.target.value }))
                }
                style={{ width: "100%" }}
              />
            )}
          </div>
        );
      })}
      <button type="submit" disabled={submitting}>
        {submitting ? "Running..." : "Run Plugin"}
      </button>
    </form>
  );
}

type FileDropzoneProps = {
  required?: boolean;
  file: File | null;
  onFile: (file: File | null) => void;
};

function FileDropzone({ required, file, onFile }: FileDropzoneProps) {
  const [dragOver, setDragOver] = useState(false);

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files?.[0];
        onFile(f ?? null);
      }}
      style={{
        border: `2px dashed ${dragOver ? "#2563eb" : "#ccc"}`,
        borderRadius: 8,
        padding: "1rem",
        background: dragOver ? "#eff6ff" : "#fafafa"
      }}
    >
      <input
        type="file"
        required={required && !file}
        onChange={(e) => onFile(e.target.files?.[0] ?? null)}
        style={{ marginBottom: "0.5rem" }}
      />
      {file ? (
        <div style={{ fontSize: "0.875rem", color: "#444" }}>
          Selected: <strong>{file.name}</strong> ({file.size} bytes)
        </div>
      ) : (
        <div style={{ fontSize: "0.875rem", color: "#666" }}>Or drag and drop a file here</div>
      )}
    </div>
  );
}
