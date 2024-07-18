# litter_assessment_service

[![Build Status](https://jenkins.services.ai4os.eu/buildStatus/icon?job=AI4OS-hub/litter-assessment/main)](https://jenkins.services.ai4os.eu/job/AI4OS-hub/job/litter-assessment/job/main/)

Integration of DeepaaS API and litter assessment software

To launch it, first install the package then run [deepaas](https://github.com/ai4os/DEEPaaS):
```bash
git clone https://github.com/ai4os-hub/litter-assessment
cd litter-assessment
pip install -e .
deepaas-run --listen-ip 0.0.0.0
```

## Project structure
```
├── LICENSE                <- License file
│
├── README.md              <- The top-level README for developers using this project.
│
├── requirements.txt       <- The requirements file for reproducing the analysis environment, e.g.
│                             generated with `pip freeze > requirements.txt`
│
├── pyproject.toml         <- makes project pip installable (pip install -e .) so
│                             litter_assessment_service can be imported
│
├── litter_assessment_service    <- Source code for use in this project.
│   │
│   ├── __init__.py        <- Makes litter_assessment_service a Python module
│   │
│   └── api.py             <- Main script for the integration with DEEP API
│
└── Jenkinsfile            <- Describes basic Jenkins CI/CD pipeline
```
