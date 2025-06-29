
# Azure Billing Records Cost Optimization (Serverless + Archival)

## 📘 Problem Statement
We operate a **read-heavy serverless billing system** built on Azure, storing over 2 million billing records in **Azure Cosmos DB**. Each record is up to **300KB** in size. However, **records older than 3 months are rarely accessed**, and the system has become increasingly expensive.

## Objective
Optimize costs while ensuring:
- ✅ Zero data loss
- ✅ No API contract changes
- ✅ Seamless transition & no downtime
- ✅ Response time for old records: seconds
- ✅ Easy maintainability

---

##  Solution Overview
We implement **hot/cold storage tiering**:
- Hot: Azure Cosmos DB for recent (≤3 months) records
- Cold: Azure Blob Storage (Cool/Archive tier) for historical records

### Architecture
![Architecture Diagram](diagrams/architecture.png)

---

## Repository Structure
```bash
azure-billing-archival/
├── README.md
├── .gitignore
├── functions/
│   ├── archive_old_records/        # Timer-triggered archival logic
│   └── retrieve_record/            # Read API with Cosmos + Blob fallback
├── infra/                          # Bicep or Terraform for Infra deployment
├── utils/                          # Reusable blob helpers
├── diagrams/                       # Architecture images
└── scripts/                        # CLI to manage blob storage
```

---

## Setup Instructions

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/azure-billing-archival.git
cd azure-billing-archival
```

### 2. Deploy Infrastructure (Example: Bicep)
```bash
az deployment group create \
  --resource-group my-rg \
  --template-file infra/main.bicep \
  --parameters @infra/parameters.json
```

### 3. Deploy Azure Functions
```bash
cd functions/archive_old_records
func azure functionapp publish <your-function-app>

cd ../retrieve_record
func azure functionapp publish <your-function-app>
```

---

## Archival Flow
- A timer-triggered function runs monthly
- Moves records older than 3 months from Cosmos DB to Blob Storage (as JSON)
- Inserts a metadata stub with blob reference into Cosmos DB

### Sample Pseudocode
```python
if record.timestamp < cutoff_date:
    blob_url = upload_to_blob(record)
    save_stub_to_cosmos(record.id, blob_url)
```

---

##  Retrieval Flow
- Read API first queries Cosmos DB
- If a stub with `archived: true` is found, download the full record from Blob Storage

---

## 💰 Cost Optimization Strategies
- Cosmos DB RUs are minimized (older data is offloaded)
- Blob Storage tiers:
  - **Hot**: short-term
  - **Cool**: long-term infrequent access
  - **Archive**: cold access, lowest cost

### Tier Management (Sample Script)
```bash
./scripts/set_blob_tier.sh archive <blob-name>
```

---

##  API Compatibility
No changes to input/output or interface. API users interact as if all data resides in Cosmos DB.

---

##  Technologies Used
- Azure Cosmos DB
- Azure Blob Storage (Cool/Archive Tier)
- Azure Functions (Timer + HTTP Trigger)
- Bicep / Terraform (for infra deployment)
- Python SDKs (Cosmos + Blob)

---

##  License
MIT

---

##  Contributions & Contact
PRs welcome. For feedback or questions, contact: `your.email@example.com`
