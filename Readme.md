# Cloud-Native Battery Data Intelligence Platform

## Project Overview

An end-to-end Data Engineering project focused on building a scalable, reproducible, and cloud-native data platform for battery performance and degradation analytics.

The platform processes publicly available lithium-ion battery aging data from NASA, transforming raw experimental measurements into structured datasets suitable for quality validation, analytics, and downstream applications.

## Problem Statement

Battery testing systems generate large volumes of time-series data, including voltage, current, temperature, capacity, and charging/discharging cycle information.

Raw experimental data often comes in complex or nested formats, making it difficult to integrate, validate, and analyze efficiently.

**Our solution:** Develop an automated data engineering pipeline that ingests battery measurements, standardizes the data, validates its quality, and prepares analysis-ready datasets.

## Dataset

**Source:** NASA Prognostics Center of Excellence — Li-ion Battery Aging Dataset

**Dataset:** [NASA Battery Aging Dataset](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/)

| Attribute | Description |
|---|---|
| Battery Type | Lithium-ion |
| Battery IDs | B0005, B0006, B0007, B0018 |
| Data Format | MATLAB `.mat` |
| Operations | Charge, Discharge, Impedance |
| Measurements | Voltage, Current, Temperature, Time, Capacity |

### Dataset Processing Results

The initial pipeline processed four battery files and produced:

| Metric | Result |
|---|---:|
| Battery files processed | 4 |
| Battery cycle records | 2,167 |
| Time-series measurement records | 2,089,050 |
| Structured output format | Apache Parquet |

These results were obtained from the initial local transformation pipeline.

## Current Architecture

```text
NASA Battery Dataset
        |
        v
Raw MATLAB Files (.mat)
        |
        v
Python + SciPy
        |
        v
Dynamic Battery File Discovery
        |
        v
NumPy + Pandas Transformation
        |
        v
Measurement Length Validation
        |
        v
Structured Parquet Datasets
```

## Implemented Features

- Downloaded and inspected NASA's public battery aging dataset.
- Loaded nested MATLAB structures using SciPy.
- Implemented dynamic discovery of battery files.
- Extracted battery cycle metadata and time-series measurements.
- Separated cycle-level records from measurement-level records.
- Added checks for mismatched measurement array lengths.
- Exported structured datasets in Apache Parquet format.

## Technology Stack

**Currently implemented**
- Python 3.11
- Pandas and NumPy
- SciPy
- Apache Parquet / PyArrow
- Git and GitHub

**Planned**
- Data quality validation and automated tests with pytest
- DVC for reproducible pipelines and data versioning
- Docker and Docker Compose
- GitHub Actions for CI/CD
- PostgreSQL and SQL analytics
- AWS S3 for cloud storage
- Apache Airflow for orchestration
- FastAPI for analytics endpoints
- Kubernetes for container orchestration
- Monitoring and performance benchmarking

## Repository Structure

```text
battery-data-platform/
├── src/
│   ├── inspect_battery.py
│   └── transform.py
├── data/
│   ├── raw/
│   └── processed/
├── config/
├── tests/
├── reports/
├── notebooks/
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

## Running the Pipeline

### 1. Create and activate the environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare the dataset

Download the NASA Battery Aging Dataset and extract the MATLAB files into:

```text
data/raw/nasa/batteries/
```

### 4. Run the transformation

```bash
python src/transform.py
```

### 5. Generated Outputs

```text
data/processed/
├── battery_cycles.parquet
└── battery_measurements.parquet
```

## Engineering Objectives

The project follows four core principles:

- **Reproducibility:** Make pipeline execution consistent and repeatable.
- **Traceability:** Track which source battery files produced each processed dataset.
- **Validation:** Identify missing, inconsistent, and invalid measurements.
- **Cost and Performance:** Benchmark processing time, resource utilization, and infrastructure costs.

## Project Status

**Current Phase:** Data Ingestion and Transformation — Completed

**Next Phase:** Data Quality Validation, Automated Testing, and DVC Integration.

This project is under active development. The README will be updated as additional capabilities are implemented.
