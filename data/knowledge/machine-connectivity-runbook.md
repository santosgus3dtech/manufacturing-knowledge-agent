# Machine Connectivity Runbook

## Observe before acting

Record the machine's last successful check, current network reachability, adapter status, and any storage or service errors before restarting anything. A dashboard timeout does not prove that the printer is offline. Separate network, application, storage, and device evidence.

## Read-only checks

Use a bounded reachability check, query the approved status endpoint, and inspect recent redacted service logs. Compare the result with another known service on the same host. Never include credentials, tokens, private addresses, or full production logs in an incident report.

## Recovery order

Preserve application data before repair when storage errors or a read-only filesystem are present. Restore the lowest-risk failed layer first: connectivity, service process, application database, then device integration. Do not combine multiple changes before validating the result.

## Closure

Close the incident only after repeated health checks pass and the machine reports a stable state. Record the original evidence, intervention, validation window, and any follow-up maintenance task.
