import type { CrmDeal, CrmUser, FormRecord } from "../api/types";
import { emptyFormPayloadV1 } from "../schemas/formV1";

export const mockUsers: CrmUser[] = [
  { id: 1, name: "Alice", email: "alice@gebras.com.br" },
  { id: 2, name: "Bob", email: "bob@gebras.com.br" },
];

export const mockDeals: CrmDeal[] = [
  { id: 746, title: "Biview", owner_id: 1, stage_id: 7, status: "open", pipeline_id: 1 },
  { id: 999, title: "Outro deal", owner_id: 1, stage_id: 7, status: "open", pipeline_id: 1 },
];

export function mockFormRecord(overrides: Partial<FormRecord> = {}): FormRecord {
  return {
    deal_id: 746,
    status: "draft",
    schema_version: "v1",
    payload: emptyFormPayloadV1(),
    owner_user_id: 1,
    owner_name: "Alice",
    deal_title: "Biview",
    ...overrides,
  };
}
