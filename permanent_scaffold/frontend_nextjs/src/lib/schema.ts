import rawSchema from "../../plugin/ui_schema.json";

/**
 * Widget types emitted by logic plugins. Aliases are normalized in DynamicForm.
 * - text_input: same as text (single-line)
 * - file_upload: browser file → { filename, mimeType, encoding, content } in payload
 */
export type FieldType =
  | "text"
  | "text_input"
  | "number"
  | "select"
  | "textarea"
  | "checkbox"
  | "file_upload";

export interface UIField {
  name: string;
  label: string;
  type: FieldType;
  required?: boolean;
  default?: string | number | boolean;
  options?: string[];
}

export interface UISchema {
  title: string;
  description: string;
  fields: UIField[];
}

export const schema = rawSchema as UISchema;
