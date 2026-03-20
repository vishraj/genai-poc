# Gen AI POC

A Proof of Concept project exploring Generative AI capabilities.

## Project Structure

```
genai-poc/
├── src/            # Backend source code (Python, API logic, AI integrations)
├── ui/             # Streamlit frontend application
├── terraform/      # Infrastructure-as-Code for cloud resources
└── sql/            # SQL scripts for database setup and queries
```

## Getting Started

### Prerequisites
- Python 3.10+
- Terraform CLI
- AWS CLI (or relevant cloud provider CLI)

### Setup

1. **Backend**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

2. **UI (Streamlit)**
   ```bash
   cd ui
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. **Infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

4. **Database**
   - Run scripts in `sql/` in the order indicated by their filename prefix.
