# Atlanta Health EDA Metrics Report

## Data Sources

- Georgia Rankable Causes Fulton and DeKalb 2024
- OASIS Rankable Causes Fulton and DeKalb 2024
- NCHS Rankable Causes Fulton and DeKalb 2024
- Georgia, OASIS, and NCHS social determinants files with education and SES vulnerability
- CMS CPSC Medicare Advantage enrollment file for Aetna contract-level enrollment
- U.S. Census ACS S0101 Age and Sex table for age 65+ population
- CVS Health Care Benefits segment revenue data, 2023-2025

## Important Method Note

NCHS is kept separate from Georgia and OASIS in combined visuals because its structure and category naming are not directly comparable. Separate NCHS charts are generated for cleaner interpretation.

## Core Mortality Metrics

- Highest total cause of death in the analysis: **Malignant Neoplasms** (2,495 deaths).
- Highest total race category in the mortality data: **Black or African-American** (17,640 deaths).
- Highest total sex category in the mortality data: **Male** (15,802 deaths).

## Top Causes by Source and County

| Source   | Geography   | Cause                                                                      |   Deaths |   Percent |
|:---------|:------------|:---------------------------------------------------------------------------|---------:|----------:|
| NCHS     | Fulton      | Malignant Neoplasms                                                        |     1409 |  24.6372  |
| NCHS     | Fulton      | Diseases of Heart                                                          |     1369 |  23.9378  |
| NCHS     | DeKalb      | Malignant Neoplasms                                                        |     1086 |  24.6538  |
| NCHS     | DeKalb      | Diseases of Heart                                                          |     1070 |  24.2906  |
| Georgia  | Fulton      | Ischemic Heart and Vascular Disease                                        |      492 |   8.67572 |
| NCHS     | Fulton      | Unintentional Injuries                                                     |      480 |   8.39308 |
| Georgia  | Fulton      | Essential (Primary) Hypertension and Hypertensive Renal, and Heart Disease |      456 |   8.04091 |
| OASIS    | Fulton      | All other Diseases of the Nervous System                                   |      455 |   8.213   |
| Georgia  | Fulton      | All Other Diseases of the Nervous System                                   |      455 |   8.02328 |
| OASIS    | Fulton      | Obstructive Heart Disease (incl. Heart Attack)                             |      428 |   7.72563 |
| Georgia  | Fulton      | Cerebrovascular Disease                                                    |      399 |   7.0358  |
| NCHS     | Fulton      | Cerebrovascular Diseases                                                   |      399 |   6.97674 |
| OASIS    | Fulton      | Stroke                                                                     |      399 |   7.20217 |
| Georgia  | DeKalb      | Ischemic Heart and Vascular Disease                                        |      399 |   9.17241 |
| NCHS     | DeKalb      | Unintentional Injuries                                                     |      369 |   8.37684 |
| OASIS    | DeKalb      | Obstructive Heart Disease (incl. Heart Attack)                             |      361 |   8.4484  |
| Georgia  | DeKalb      | Essential (Primary) Hypertension and Hypertensive Renal, and Heart Disease |      342 |   7.86207 |
| OASIS    | DeKalb      | All other Diseases of the Nervous System                                   |      340 |   7.95694 |
| Georgia  | DeKalb      | All Other Diseases of the Nervous System                                   |      340 |   7.81609 |
| NCHS     | Fulton      | Alzheimer's Disease                                                        |      313 |   5.47298 |
| Georgia  | Fulton      | Alzheimers Disease                                                         |      313 |   5.51931 |
| OASIS    | Fulton      | Alzheimer's Disease                                                        |      313 |   5.64982 |
| OASIS    | Fulton      | Hypertensive Heart Disease                                                 |      298 |   5.37906 |
| NCHS     | DeKalb      | Cerebrovascular Diseases                                                   |      289 |   6.56073 |
| OASIS    | DeKalb      | Stroke                                                                     |      289 |   6.7634  |
| Georgia  | DeKalb      | Cerebrovascular Disease                                                    |      289 |   6.64368 |
| OASIS    | DeKalb      | Hypertensive Heart Disease                                                 |      243 |   5.68687 |
| Georgia  | DeKalb      | Alzheimers Disease                                                         |      222 |   5.10345 |
| OASIS    | DeKalb      | Alzheimer's Disease                                                        |      222 |   5.19541 |
| NCHS     | DeKalb      | Alzheimer's Disease                                                        |      222 |   5.03973 |

## Social Determinants Metrics

| Source   | Geography   | Education                 | SES Vulnerability                | Race                 | Cause                                                                      |   Deaths |
|:---------|:------------|:--------------------------|:---------------------------------|:---------------------|:---------------------------------------------------------------------------|---------:|
| Georgia  | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Ischemic Heart and Vascular Disease                                        |      930 |
| OASIS    | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | All other Diseases of the Nervous System                                   |      892 |
| Georgia  | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | All Other Diseases of the Nervous System                                   |      892 |
| NCHS     | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | All other Diseases of the Nervous System                                   |      892 |
| Georgia  | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Essential (Primary) Hypertension and Hypertensive Renal, and Heart Disease |      886 |
| NCHS     | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Obstructive Heart Disease (incl. Heart Attack)                             |      812 |
| OASIS    | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Obstructive Heart Disease (incl. Heart Attack)                             |      812 |
| Georgia  | DeKalb      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Ischemic Heart and Vascular Disease                                        |      774 |
| OASIS    | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Stroke                                                                     |      764 |
| NCHS     | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Stroke                                                                     |      764 |
| Georgia  | Fulton      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Cerebrovascular Disease                                                    |      764 |
| OASIS    | DeKalb      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Obstructive Heart Disease (incl. Heart Attack)                             |      698 |
| NCHS     | DeKalb      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | Obstructive Heart Disease (incl. Heart Attack)                             |      698 |
| OASIS    | DeKalb      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | All other Diseases of the Nervous System                                   |      668 |
| Georgia  | DeKalb      | Selected Educations Total | Selected SES Vulnerability Total | Selected Races Total | All Other Diseases of the Nervous System                                   |      668 |

## Aetna Medicare Advantage Enrollment

| County   |   Known Enrollment |   Suppressed Rows |   Plan Rows |   Max Suppressed Enrollment |   Minimum Possible Total |   Maximum Possible Total |
|:---------|-------------------:|------------------:|------------:|----------------------------:|-------------------------:|-------------------------:|
| DEKALB   |               6734 |                18 |          22 |                         180 |                     6734 |                     6914 |
| FULTON   |               9530 |                19 |          23 |                         190 |                     9530 |                     9720 |
| COMBINED |              16264 |                37 |          45 |                         370 |                    16264 |                    16634 |

## Age 65+ Market Opportunity

| County   |   Age 65+ Population |   Known Enrollment |   Penetration Rate |   Remaining Opportunity |
|:---------|---------------------:|-------------------:|-------------------:|------------------------:|
| DEKALB   |               112767 |               6734 |            5.97161 |                  106033 |
| FULTON   |               146945 |               9530 |            6.48542 |                  137415 |

## CVS Health Care Benefits Forecast

### Revenue Forecast

| Scenario     |   Year |   Growth Rate Used |   Forecast Total Revenue Millions |
|:-------------|-------:|-------------------:|----------------------------------:|
| Conservative |   2026 |          0.0824362 |                            155172 |
| Conservative |   2027 |          0.0824362 |                            167963 |
| Conservative |   2028 |          0.0824362 |                            181810 |
| Base         |   2026 |          0.164872  |                            166989 |
| Base         |   2027 |          0.164872  |                            194521 |
| Base         |   2028 |          0.164872  |                            226592 |
| Aggressive   |   2026 |          0.206091  |                            172898 |
| Aggressive   |   2027 |          0.206091  |                            208531 |
| Aggressive   |   2028 |          0.206091  |                            251507 |

### Potential Aetna Market Opportunity

| County   |   Capture Rate |   Potential Members |   Revenue Per Member Assumption |   Incremental Revenue |   Incremental Revenue Millions |
|:---------|---------------:|--------------------:|--------------------------------:|----------------------:|-------------------------------:|
| DEKALB   |           0.01 |             1060.33 |                            5391 |           5.71624e+06 |                        5.71624 |
| DEKALB   |           0.03 |             3180.99 |                            5391 |           1.71487e+07 |                       17.1487  |
| DEKALB   |           0.05 |             5301.65 |                            5391 |           2.85812e+07 |                       28.5812  |
| FULTON   |           0.01 |             1374.15 |                            5391 |           7.40804e+06 |                        7.40804 |
| FULTON   |           0.03 |             4122.45 |                            5391 |           2.22241e+07 |                       22.2241  |
| FULTON   |           0.05 |             6870.75 |                            5391 |           3.70402e+07 |                       37.0402  |

## Generated Outputs

- Separate health burden heatmaps by source and county
- Combined Georgia/OASIS pie chart dashboards
- Separate NCHS pie chart dashboards
- Education and SES heatmaps by source and county
- Sunburst charts for Georgia/OASIS and separate NCHS sunburst charts
- Aetna enrollment chart
- Age 65+ market opportunity dashboard
- CVS revenue forecast charts
- Aetna market opportunity revenue chart
