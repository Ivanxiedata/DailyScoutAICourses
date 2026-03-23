import rawSchema from "../../../plugin/ui_schema.json";

export type FieldType = "text" | "number" | "select" | "textarea" | "checkbox";

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
