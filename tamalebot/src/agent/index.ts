// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 TamaleBot Contributors

/**
 * Agent Runtime
 *
 * This is the process that runs inside each agent's Docker container.
 * It connects to the LLM, receives instructions, executes tool calls
 * (after security policy checks), and reports results.
 *
 * Each agent container runs one instance of this process.
 */

import { PolicyEngine } from "../security/policy-engine.js";
import { AuditTrail } from "../security/audit-trail.js";
import { SecretManager } from "../security/secret-manager.js";

const agentId = process.env.TAMALEBOT_AGENT_ID ?? "standalone";
const policyName = process.env.TAMALEBOT_POLICY ?? "default";

const policy = new PolicyEngine();
const audit = new AuditTrail("/app/data/logs", agentId);
const secrets = new SecretManager(audit);

console.log(`[tamalebot-agent] Agent ${agentId} starting`);
console.log(`[tamalebot-agent] Policy: ${policyName}`);
console.log(`[tamalebot-agent] Waiting for connections...`);

// Agent runtime will be expanded in Phase 1:
// - LLM connection (Anthropic/OpenAI via user's API key)
// - MCP tool server registration
// - Integration bridges (Telegram, Slack)
// - Tool call interception via policy engine

process.on("SIGTERM", () => {
  console.log(`[tamalebot-agent] Agent ${agentId} shutting down`);
  audit.close();
  process.exit(0);
});

process.on("SIGINT", () => {
  console.log(`[tamalebot-agent] Agent ${agentId} interrupted`);
  audit.close();
  process.exit(0);
});
