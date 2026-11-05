# Integration map

## Calls between workflows

| From | To | How | Payload |
|------|----|-----|---------|
| 01 (node *Trigger Account Provisioning*) | 02 | HTTP POST `/webhook/hris-lifecycle` | `event: "Hire"`, worker ID, names, department, title, manager, start date |
| 05 (node *Trigger Deprovisioning*) | 02 | HTTP POST `/webhook/hris-lifecycle` | `event: "Terminate"`, worker ID, full name, work email, department, effective date |

Workflow 02 uses an AI extractor to normalize any HRIS payload, so these calls and your real HRIS webhooks share one entry point.

## External systems

| System | Used by | Notes |
|--------|---------|-------|
| ATS (Greenhouse, Lever, Workable, Ashby) | 01 | Offer accepted webhook |
| HRIS (Workday, BambooHR, HiBob) | 01, 02, 03, 04, 05, 06 | Replace the generic HTTP nodes with native nodes where available |
| Microsoft Entra ID | 02 | Create, update, disable users |
| Google Workspace | 02 | Create and suspend users |
| Slack / Microsoft Teams | all | Notifications, escalations, approvals |
| Gmail / Outlook | 01, 03, 04, 05, 06 | Email and approvals |
| Timekeeping (Clockify, Deputy, Jibble, biometric) | 03, 06 | Timesheets and attendance metrics |
| LMS | 06 | Mandatory training assignments |
| Google Sheets | 01, 04, 05, 06 | Logs and trackers. Replace with Notion, Jira or a database if preferred |
