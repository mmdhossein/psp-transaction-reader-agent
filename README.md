# PSP Transaction Agent

A CSV-based chat agent for analyzing payment transactions — built on Semantic Kernel + Gradio. Upload a transactions CSV, ask questions in plain english, get answers about volume, fraud, reconciliation, and more.

## What it does

You give it a CSV of PSP transactions, it loads and validates the data, then you can just chat with it like:

- "what's the success rate for merchant M123?"
- "show me suspicious transactions from last week"
- "reconcile totals for all merchants"
- "which payment method has highest failure rate?"

Under the hood its just a kernel with a bunch of plugins registered, and the LLM decides which function to call based on what you asked.

## Project structure

psp-transaction-agent/
├── main.py                        # entrypoint, gradio UI
├── src/
│   ├── core/
│   │   ├── kernel_manager.py      # sets up semantic kernel + LLM connection
│   │   └── chat_manager.py        # chat history handling
│   ├── models/
│   │   ├── enums.py                # TransactionStatus, Currency, etc
│   │   └── transaction.py          # Transaction dataclass
│   ├── plugins/
│   │   ├── transaction_plugin.py   # core stats: summary, breakdowns, search
│   │   ├── analytics_plugin.py     # trends, geo, cohorts
│   │   ├── fraud_plugin.py         # suspicious pattern detection
│   │   └── reconciliation_plugin.py # settlement + discrepancy checks
│   └── utils/
│       ├── csv_loader.py           # load + clean csv
│       ├── validators.py           # row-level validation
│       └── formatters.py           # currency/date/table formatting
└── tests/


## Setup

```bash
git clone <your-repo-url>
cd psp-transaction-agent
python -m venv venv
source venv/bin/activate   # windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your OpenAI/Azure OpenAI creds:

OPENAI_API_KEY=your-key-here
OPENAI_MODEL_ID=gpt-4o
# or for azure:
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...


Then just run it:

```bash
python main.py
```

Opens up a gradio app in your browser, upload a csv and start chatting.

## CSV format

Your csv needs at minimum these columns (names matter, case-insensitive-ish handled in the loader):

| column | required | notes |
|---|---|---|
| transaction_id | yes | must be unique |
| merchant_id | yes | |
| amount | yes | numeric |
| currency | yes | USD, EUR, GBP, IRR, AED |
| status | yes | success, failed, pending, refunded etc |
| created_at | yes | most common date formats work |
| payment_method | no | card, wallet, bank_transfer... |
| customer_id | no | needed for cohort/search stuff |
| country | no | needed for geo breakdown |

If a row fails validation it gets skipped (not crash the whole load), you'll see a count of skipped rows after upload.

## Plugins, briefly

- **TransactionPlugin** — the basics, totals, status breakdown, merchant ranking, search by id
- **AnalyticsPlugin** — trends over time, currency/geo splits, hourly patterns, cohorts
- **FraudPlugin** — flags velocity spikes, oddly large amounts, weird failed→success patterns, chargebacks
- **ReconciliationPlugin** — gross vs net vs settled per merchant, duplicate ids, refund anomalies

Each one is just registered as a kernel plugin so the model calls them automatically depending what you ask, you don't need to pick manually.

## Known limitations

- No persistence — reload the csv every session
- Fraud detection is heuristic based, not ML, so treat it as a starting point not gospel
- Large CSVs (500k+ rows) will be slow, pandas ops aren't optimized for that yet

## Contributing

PRs welcome. Try to keep plugin functions small and single-purpose, and add validation for any new required column.

---

Built with [Semantic Kernel](https://github.com/microsoft/semantic-kernel) and [Gradio](https://gradio.app).