# Setup guide

## 1. Activation order

1. `02-hris-lifecycle-identity` (called by 01 and 05)
2. `01-recruitment-to-onboarding`
3. `05-offboarding`
4. `04-employee-self-service`
5. `03-time-attendance-payroll`
6. `06-performance-learning-reporting`

Activate a workflow only after it passes a test run. Webhooks and forms use their **Production URL** once active, and the **Test URL** while you press *Listen for test event*.

## 2. Credentials per workflow

Create these in n8n under **Credentials**. Workflow files contain no credentials, so open each node with a red warning and select one.

| Workflow | LLM | Gmail | Slack | Google Sheets | Other |
|----------|:---:|:-----:|:-----:|:-------------:|-------|
| 01 Recruitment to Onboarding | x | x | x | x | Header Auth (webhook), HRIS API |
| 02 HRIS Lifecycle | x | | x | | Header Auth (webhook), Microsoft Entra ID, Google Workspace Admin |
| 03 Time, Attendance, Payroll | x | x | x | | Timekeeping API, HRIS API |
| 04 Employee Self-Service | x | x | x | x | Header Auth (webhook), HRIS API |
| 05 Offboarding | x | x | x | x | Header Auth (webhook), HRIS API |
| 06 Performance, Learning, Reporting | x | x | x | x | HRIS, LMS and timekeeping APIs |

The LLM node defaults to OpenAI (`gpt-4o-mini`). Swap it for Anthropic, Azure OpenAI or another chat model by replacing the model sub-node.

## 3. Placeholders

```bash
python scripts/validate.py --placeholders
```

Common ones: `YOUR-HRIS.example.com`, `YOUR-TIMEKEEPING.example.com`, `YOUR-LMS.example.com`, `YOUR-N8N-URL`, `YOUR_TOKEN`, `YOUR_SHEET_ID`, `YOUR_HEADER_AUTH_VALUE`, plus email addresses and Slack channel names.

## 4. Google Sheets to create

| Sheet (tab) | Used by | Columns |
|-------------|---------|---------|
| `Onboarding` | 01 | Candidate ID, Name, Role, Department, Manager, Start Date, Contract Signed, Equipment Ordered, Accounts Provisioned, Orientation Scheduled |
| `Tickets` | 04 | Ticket ID, Created, Employee ID, Employee, Category, Details, Owner Team, SLA, Status |
| `Audit` | 04 | Timestamp, Employee ID, Category, Outcome |
| `Offboarding` | 05 | Employee ID, Name, Department, Type, Last Working Day, Final Pay Due, Started, Status |
| `ExitInterviews` | 05 | Date, Reason, Manager Rating, Recommend, Sentiment, Themes, Summary |
| `SelfReviews` | 06 | Date, Cycle, Employee ID, Name, Goals Progress, Engagement, Strengths, Growth Areas, Summary |
| `ManagerReviews` | 06 | Date, Cycle, Employee ID, Name, Rating, Recommendation, Status |
| `KPI History` | 06 | Date, Headcount, Joiners 30d, Leavers 30d, Turnover 30d %, Absence %, Overtime Hours, Review Completion %, Training Compliance % |

Restrict `SelfReviews`, `ManagerReviews` and `ExitInterviews` to HR only.

## 5. Webhook and form paths

| Workflow | Type | Path |
|----------|------|------|
| 01 | Webhook | `/webhook/ats-offer-accepted` |
| 02 | Webhook | `/webhook/hris-lifecycle` |
| 04 | Webhook | `/webhook/hr-request` |
| 05 | Webhook | `/webhook/hris-offboarding` |
| 05 | Form | `/form/exit-interview` |
| 06 | Form | `/form/self-review` and `/form/manager-review` |

Webhooks use **Header Auth**. Create a Header Auth credential, for example header `X-API-Key`, and send the same header from your HRIS, ATS or chat integration.

## 6. Testing with sample payloads

Use the Test URL while the webhook node is listening:

```bash
curl -X POST "https://YOUR-N8N-URL/webhook-test/hris-lifecycle" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_HEADER_AUTH_VALUE" \
  -d @samples/hris-lifecycle.json
```

Replace `webhook-test/<path>` with the path for each workflow and use the matching file in `samples/`. While testing, deactivate nodes that touch real systems (Entra ID, Google Workspace, payroll email, HRIS writes).

## 7. Known caveats

- **Send and Wait** (Gmail approvals in 03/04/05) and **hidden form fields** (06) depend on your n8n version. Verify parameter names in the UI.
- **Timezone** is set to `Asia/Manila` in each workflow's settings. Change it in *Workflow settings*.
- **Wait nodes** hold executions open until the target date or response. Add timeouts where appropriate.
- **API response shapes** are assumptions (documented in node notes). Adjust the Code nodes to match your systems, and add a Split Out node if an API wraps arrays in an object.
- **Rate limits:** for large headcounts, add Loop Over Items with a short Wait before bulk email sends.
