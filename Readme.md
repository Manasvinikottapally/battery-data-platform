
# Cloud-Native Battery Data Intelligence Platform

A data engineering project for processing, validating, versioning, and analyzing lithium-ion battery aging data using Python, Apache Parquet, DVC, and modern data infrastructure.

## 1. Project Overview

Battery testing systems generate large volumes of experimental data, including voltage, current, temperature, discharge capacity, and charge/discharge cycle information.

These measurements are often stored in complex scientific file formats that are not immediately suitable for SQL analytics, dashboards, or cloud-based applications.

This project aims to build an automated, reproducible data platform that converts raw battery data into structured, quality-checked datasets and eventually supports cloud storage, workflow orchestration, APIs, and battery degradation analytics.

The current implementation includes a local ETL pipeline, data-quality checks, SHA-256 source verification, curated datasets, and DVC-based data versioning and pipeline execution.

## 2. Problem Statement

Raw battery datasets present several engineering challenges:

- Nested scientific data formats make direct analysis difficult
- Manual processing does not scale as more battery files are added
- Missing or unusual measurements can affect downstream analysis
- Without data lineage, it is difficult to reproduce and verify results
- Large time-series datasets require efficient storage and processing
- Dataset changes can produce inconsistent results if source files are not verified

**Solution:** Develop a modular ETL pipeline with dynamic file discovery, standardized schemas, data validation, integrity verification, reproducible processing, and analytics-ready storage.

## 3. Dataset

**Source:** NASA Prognostics Center of Excellence — Li-ion Battery Aging Dataset

Dataset reference:
https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/

The initial implementation uses four battery files:

- B0005
- B0006
- B0007
- B0018

The dataset contains charge, discharge, and impedance operations. Available measurements include battery voltage, current, temperature, elapsed time, and discharge capacity.

### Processing Results

| Metric | Value |
|---|---:|
| Battery files processed | 4 |
| Total cycle records | 2,167 |
| Time-series measurement records | 2,089,050 |
| Primary output format | Apache Parquet |

These counts were obtained from the executed transformation pipeline.

## 4. Current Architecture

```text
NASA Li-ion Battery Dataset
          |
          v
Raw MATLAB Files (.mat)
          |
          +----> SHA-256 Manifest
          |           |
          |           v
          |      File Integrity Verification
          |
          v
Dynamic File Discovery (pathlib)
          |
          v
MATLAB Data Extraction (SciPy)
          |
          v
Data Transformation (NumPy + Pandas)
          |
          v
Structured Parquet Datasets
          |
          +----> Data Quality Validation
          |
          +----> Data Curation
                       |
                       +--> Passing Measurements
                       |
                       +--> Flagged Measurements

DVC:
- Tracks raw battery dataset versions
- Defines transform, validate, and curate stages
- Records stage dependencies and output hashes
- Supports incremental pipeline reproduction
```

The current validation and curation stages share transformed datasets as dependencies. A strict validation-before-curation dependency will be added through a persistent quality-report stage.

## 5. Implemented Features

### 5.1 Data Ingestion and Transformation

- Read nested NASA MATLAB battery files using SciPy
- Automatically discover `B*.mat` files without hardcoding battery IDs
- Extract charge, discharge, and impedance cycle metadata
- Extract voltage, current, temperature, and elapsed-time measurements for charge and discharge operations
- Preserve discharge capacity values
- Validate measurement array lengths before constructing records
- Generate separate cycle-level and measurement-level datasets

**Script:** `src/transform.py`

**Outputs:**

- `data/processed/battery_cycles.parquet`
- `data/processed/battery_measurements.parquet`

### 5.2 Data Storage

- Store transformed datasets in Apache Parquet format
- Preserve `battery_id` and `cycle_id` for joining related records
- Separate raw, processed, and curated data directories
- Preserve original source files for reproducibility

### 5.3 Data Quality Validation

- Identify missing measurement values
- Check duplicate cycle identifiers
- Validate supported cycle types
- Check discharge capacity values
- Identify orphan measurements
- Flag voltage readings outside a provisional 0–6 V screening range
- Investigate the locations and patterns of anomalies

**Scripts:**

- `src/validate.py`
- `src/investigate_anomalies.py`

### 5.4 Data Provenance and Integrity Verification

Implemented SHA-256-based file verification to detect changes to the original battery dataset.

**Scripts:**

- `src/create_manifest.py`
- `src/verify_manifest.py`

The manifest records:

- Battery identifier
- Source file path
- File size
- SHA-256 checksum
- Dataset source
- Manifest generation timestamp

**Output:**

`data/manifest.json`

The verification script recalculates file hashes and compares them with the recorded manifest.

Missing files, checksum mismatches, and file-size mismatches are reported.

An unexpected mismatch must be investigated before approving a new source-data version.

### 5.5 Data Curation

Implemented a curation stage that separates measurements according to the current data-quality screening rules.

**Script:** `src/clean.py`

**Outputs:**

- `data/curated/battery_measurements_clean.parquet`
- `data/curated/battery_measurements_flagged.parquet`

Flagged records are preserved rather than permanently deleted.

The preliminary rules flag measurements with missing sensor values or voltages outside the provisional screening range.

These rules are intended for initial quality investigation and do not establish scientific validity.

### 5.6 Data Versioning with DVC

Integrated Data Version Control (DVC) alongside Git.

**Git tracks:**

- Python source code
- Configuration files
- README and documentation
- DVC metadata
- Pipeline definitions

**DVC manages:**

- Raw dataset versions
- Data-processing dependencies
- Versioned pipeline outputs
- Incremental pipeline execution

The raw NASA dataset is tracked using:

`data/raw/nasa/batteries.dvc`

The repository also contains:

- `.dvc/`
- `dvc.yaml`
- `dvc.lock`

Remote DVC storage has not yet been configured.

### 5.7 Reproducible ETL Pipeline

The `dvc.yaml` pipeline currently defines three stages.

| Stage | Responsibility |
|---|---|
| transform | Verify the source manifest and transform MATLAB files into Parquet |
| validate | Run data-quality checks on processed datasets |
| curate | Separate passing and flagged measurements |

DVC records the dependencies and outputs in `dvc.lock`.

When no relevant changes are detected, DVC skips unchanged stages, avoiding unnecessary reprocessing.

**Run the pipeline:**

```bash
python -m dvc repro
```

**Check pipeline status:**

```bash
python -m dvc status
```

The pipeline has been verified locally as up to date. Full fresh-clone reproducibility will be tested after configuring remote dataset storage and automated tests.

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

These observations are flagged for further investigation.

The voltage threshold is an exploratory screening rule, not a validated universal specification.

The original measurements are retained to support reproducibility and further analysis.

## 7. Technology Stack

### Currently Used

| Technology | Purpose |
|---|---|
| Python 3.11 | Main ETL implementation |
| SciPy | MATLAB file extraction |
| NumPy | Numeric array processing |
| Pandas | Data transformation and validation |
| Apache Parquet / PyArrow | Columnar data storage |
| SHA-256 / hashlib | File integrity verification |
| DVC | Dataset versioning and reproducible pipelines |
| Git and GitHub | Source code and metadata version control |

### Planned Integrations

| Technology | Purpose |
|---|---|
| pytest | Automated pipeline and data-quality tests |
| Docker | Containerized pipeline execution |
| GitHub Actions | Continuous integration |
| PostgreSQL | Structured analytics queries |
| AWS S3 | Remote dataset and cloud object storage |
| Apache Airflow | Workflow scheduling and orchestration |
| FastAPI | Battery analytics and data-access APIs |
| Terraform | Infrastructure as Code |
| Monitoring tools | Pipeline observability and failure diagnostics |
| Kubernetes | Optional container orchestration, if warranted |

## 8. Project Structure

```text
battery-data-platform/
├── src/
│   ├── inspect_battery.py
│   ├── transform.py
│   ├── validate.py
│   ├── investigate_anomalies.py
│   ├── create_manifest.py
│   ├── verify_manifest.py
│   └── clean.py
├── data/
│   ├── raw/
│   │   └── nasa/
│   │       ├── batteries/
│   │       └── batteries.dvc
│   ├── processed/
│   ├── curated/
│   └── manifest.json
├── .dvc/
├── .dvcignore
├── dvc.yaml
├── dvc.lock
├── requirements.txt
├── .gitignore
└── README.md
```

Large datasets are excluded from ordinary Git tracking.

## 9. Local Setup

### 9.1 Clone the Repository

```bash
git clone https://github.com/Manasvinikottapally/battery-data-platform.git
cd battery-data-platform
```

### 9.2 Create a Python Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install dvc
```

The current DVC pipeline assumes a local environment at `.venv/`. Improving cross-machine command portability is part of the reproducibility work.

### 9.3 Prepare the Raw Dataset

Download the NASA Li-ion Battery Aging Dataset.

Extract the four selected MATLAB files into:

`data/raw/nasa/batteries/`

The files must match the recorded manifest.

A DVC remote is planned so future setups can retrieve the exact tracked dataset using `dvc pull`.

### 9.4 Verify Source Integrity

```bash
python src/verify_manifest.py
```

The script compares source files against the recorded SHA-256 manifest.

### 9.5 Run the Full DVC Pipeline

```bash
python -m dvc repro
```

This executes the configured transformation, validation, and curation stages when their dependencies have changed.

### 9.6 Verify Pipeline Status

```bash
python -m dvc status
```

When all tracked dependencies and outputs match their recorded states, DVC reports:

```text
Data and pipelines are up to date.
```

### 9.7 Run Individual Scripts

For development or debugging:

```bash
python src/transform.py
python src/validate.py
python src/investigate_anomalies.py
python src/clean.py
```

The DVC pipeline is the preferred execution method for reproducible processing.

## 10. Engineering Principles

### Reproducibility

Associate known source datasets with processing code and tracked outputs.

### Traceability

Preserve battery identifiers, cycle relationships, source metadata, and dataset versions.

### Data Quality

Detect and investigate missing, unusual, or inconsistent measurements without silently deleting source data.

### Modularity

Keep ingestion, transformation, validation, and curation as separate components.

### Performance and Cost Awareness

Avoid unnecessary recomputation and prepare to measure pipeline runtime, resource usage, and cloud infrastructure costs.

## 11. Development Roadmap

### Data Foundation

- [x] Set up project environment
- [x] Download and inspect NASA data
- [x] Implement dynamic file discovery
- [x] Build MATLAB-to-Parquet transformation
- [x] Generate structured datasets
- [x] Run initial data-quality validation
- [x] Investigate anomalies
- [x] Implement data curation
- [x] Create SHA-256 dataset manifest
- [x] Verify original source files

### Pipeline Reproducibility

- [x] Initialize DVC
- [x] Track the raw NASA dataset with DVC
- [x] Create DVC transform stage
- [x] Create DVC validation stage
- [x] Create DVC curation stage
- [x] Verify local DVC pipeline status
- [ ] Generate persistent data-quality reports
- [ ] Add automated pytest coverage
- [ ] Enforce validation before curation
- [ ] Configure and test DVC remote storage
- [ ] Verify reproducibility from a fresh clone

### Cloud and Backend Development

- [ ] Containerize processing using Docker
- [ ] Configure GitHub Actions CI
- [ ] Integrate AWS S3
- [ ] Implement SQL analytics with PostgreSQL
- [ ] Add Apache Airflow workflow orchestration
- [ ] Build battery degradation analytics
- [ ] Develop FastAPI REST endpoints
- [ ] Add monitoring and logging
- [ ] Benchmark pipeline performance
- [ ] Document infrastructure costs

### Future Enhancements

- [ ] Battery aging trend visualization
- [ ] Battery comparison dashboard
- [ ] Research-document retrieval and grounded Q&A
- [ ] Cloud deployment with Infrastructure as Code

## 12. Current Status

**Phase 1 — Data Ingestion and Transformation: Completed**

**Phase 2 — Data Quality and Curation: Initial implementation completed**

**Phase 3 — Data Versioning and Local DVC Pipeline: Completed**

**Next Focus — Automated Data Quality Testing, Persistent Reports, and Remote Storage**

The project is actively being developed as a portfolio demonstrating Data Engineering, backend engineering, reproducibility, and cloud infrastructure practices.
