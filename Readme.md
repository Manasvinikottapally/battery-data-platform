# Cloud-Native Battery Data Intelligence Platform

A data engineering project for processing, validating, and analyzing lithium-ion battery aging data using Python and modern data infrastructure.

## 1. Project Overview

Battery testing systems generate large volumes of experimental data, including voltage, current, temperature, discharge capacity, and charge/discharge cycle information.

These measurements are often stored in complex scientific file formats that are not immediately suitable for SQL analytics, dashboards, or cloud-based applications.

This project aims to build an automated, reproducible data platform that converts raw battery data into structured, quality-checked datasets and eventually supports cloud storage, orchestration, and battery degradation analytics.

## 2. Problem Statement

Raw battery datasets present several engineering challenges:

- Nested scientific data formats make direct analysis difficult
- Manual processing does not scale as more battery files are added
- Missing or unusual measurements can affect downstream analysis
- Without data lineage, it is difficult to reproduce and verify results
- Large time-series datasets require efficient storage and processing

**Solution:** Develop a modular ETL pipeline with dynamic file discovery, standardized schemas, data validation, and analytics-ready storage.

## 3. Dataset

**Source:** NASA Prognostics Center of Excellence — Li-ion Battery Aging Dataset

Dataset reference: https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/

The initial implementation uses four battery files:

- B0005
- B0006
- B0007
- B0018

The dataset contains charge, discharge, and impedance operations. Measurements include battery voltage, current, temperature, elapsed time, and discharge capacity.

### Processing Results

| Metric | Value |
|---|---:|
| Battery files processed | 4 |
| Total cycle records | 2,167 |
| Time-series measurement records | 2,089,050 |
| Output format | Apache Parquet |

These counts were obtained from the successfully executed transformation pipeline.

## 4. Current ETL Architecture

NASA Battery Dataset (.mat)
↓
Dynamic File Discovery (Python pathlib)
↓
MATLAB Extraction (SciPy)
↓
Data Transformation (NumPy + Pandas)
↓
Structured Cycle and Measurement Tables
↓
Apache Parquet Storage
↓
Data Quality Validation and Anomaly Investigation

A curated analytics layer has been implemented in code and is pending execution verification.

## 5. Implemented Features

### Data ingestion and transformation

- Read nested NASA MATLAB battery files using SciPy
- Automatically discover `B*.mat` files without hardcoding battery IDs
- Extract charge, discharge, and impedance cycle metadata
- Extract voltage, current, temperature, and elapsed-time measurements for charge and discharge operations
- Preserve discharge capacity values
- Validate measurement array lengths before constructing records
- Generate separate cycle-level and measurement-level datasets

### Data storage

- Store transformed datasets in Apache Parquet format
- Preserve `battery_id` and `cycle_id` for joining related data
- Separate raw input files from processed output files

### Data quality

- Identify missing measurement values
- Check duplicate cycle identifiers
- Validate supported cycle types
- Check discharge capacity values
- Identify orphan measurements
- Flag voltage readings outside a provisional 0–6 V screening range
- Investigate the locations and patterns of anomalies

## 6. Data Quality Findings

Validation of 2,089,050 measurement records produced:

| Validation Check | Result |
|---|---:|
| Rows with missing sensor measurements | 2 |
| Voltage readings outside 0–6 V | 4 |
| Duplicate cycle identifiers | 0 |
| Invalid cycle types | 0 |
| Invalid discharge capacities | 0 |
| Orphan measurements | 0 |

### Anomaly Investigation

- B0018, cycle 115: two charging records with missing voltage, current, and temperature
- B0005, cycle 85: high voltage reading at the start of charging
- B0006, cycle 85: high voltage reading at the start of charging
- B0006, cycle 616: slightly negative voltage reading
- B0007, cycle 85: high voltage reading at the start of charging

These observations are flagged for further investigation. The voltage threshold is an exploratory screening rule, not a validated universal specification.

The original measurements are retained to support reproducibility and further analysis.

## 7. Technology Stack

### Currently used

| Technology | Purpose |
|---|---|
| Python 3.11 | Main pipeline implementation |
| SciPy | MATLAB file extraction |
| NumPy | Numeric array processing |
| Pandas | Data transformation and validation |
| Apache Parquet / PyArrow | Columnar data storage |
| Git and GitHub | Version control |

### Planned integrations

| Technology | Purpose |
|---|---|
| pytest | Automated data and pipeline testing |
| DVC | Data and pipeline reproducibility |
| Docker | Containerized execution |
| GitHub Actions | Continuous integration |
| PostgreSQL | Structured analytics queries |
| AWS S3 | Cloud object storage |
| Apache Airflow | Workflow orchestration |
| FastAPI | Data access and analytics APIs |
| Kubernetes | Container orchestration, if warranted by deployment needs |

## 8. Project Structure

```text
battery-data-platform/
├── src/
│   ├── inspect_battery.py
│   ├── transform.py
│   ├── validate.py
│   ├── investigate_anomalies.py
│   └── clean.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── curated/
├── requirements.txt
├── .gitignore
└── README.md
```

Some files and folders, including `clean.py` and the curated outputs, may not yet have been executed or verified locally.

## 9. Local Setup

### Clone the repository

```bash
git clone https://github.com/Manasvinikottapally/battery-data-platform.git
cd battery-data-platform
```

### Create the Python environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Prepare the input data

Download the NASA Li-ion Battery Aging Dataset and extract the selected MATLAB files into:

`data/raw/nasa/batteries/`

### Run the transformation

```bash
python src/transform.py
```

Expected processed outputs:

- `data/processed/battery_cycles.parquet`
- `data/processed/battery_measurements.parquet`

### Run data validation

```bash
python src/validate.py
```

### Investigate anomalies

```bash
python src/investigate_anomalies.py
```

### Generate curated outputs

```bash
python src/clean.py
```

This last command is the next execution step to verify. The script is intended to generate:

- `data/curated/battery_measurements_clean.parquet`
- `data/curated/battery_measurements_flagged.parquet`

## 10. Engineering Principles

The project is being developed around four key principles:

**Reproducibility:** Make it possible to rerun processing and reproduce results from known inputs.

**Traceability:** Track input files, transformations, and resulting datasets.

**Data quality:** Detect and document missing, unexpected, or inconsistent measurements.

**Performance and cost awareness:** Measure pipeline runtime, resource usage, and future infrastructure costs.

## 11. Development Roadmap

- [x] Set up project environment
- [x] Download and inspect NASA data
- [x] Implement dynamic file discovery
- [x] Build MATLAB-to-Parquet transformation pipeline
- [x] Generate structured datasets
- [x] Run data-quality validation
- [x] Investigate anomalies
- [ ] Verify curated-data generation
- [ ] Add automated pytest coverage
- [ ] Add DVC pipeline tracking and dataset manifests
- [ ] Containerize the pipeline with Docker
- [ ] Configure GitHub Actions CI
- [ ] Integrate PostgreSQL for SQL analytics
- [ ] Add AWS S3 storage
- [ ] Implement workflow orchestration
- [ ] Build battery degradation analytics and API endpoints
- [ ] Benchmark pipeline performance and document cloud costs

## 12. Current Status

**Phase 1 — Data Ingestion and Transformation: Completed**

**Phase 2 — Data Quality Investigation: Completed initial checks**

**Next focus — Curated Data Verification and Automated Testing**

This project is actively being developed as a practical portfolio project demonstrating Data Engineering, backend engineering, automation, and cloud infrastructure skills.
