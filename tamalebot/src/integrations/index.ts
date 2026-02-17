// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 TamaleBot Contributors

/**
 * Integration Layer
 *
 * Each integration is an MCP (Model Context Protocol) server that
 * connects the agent to external services. Integrations are open
 * source so the community can add more.
 *
 * Phase 1: Telegram, Web browsing
 * Phase 2: Email (Gmail), Slack, Calendar
 * Phase 3: Discord, WhatsApp
 * Phase 4: iMessage (via relay)
 */

export interface Integration {
  name: string;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  isConnected(): boolean;
}

// Integration implementations will be added in Phase 1
