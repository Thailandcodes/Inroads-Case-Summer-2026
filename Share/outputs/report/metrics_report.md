# Atlanta Health EDA Metrics Report

## Executive Summary

This report tells the full project story from health burden to business opportunity. It begins by identifying the leading causes of death in Fulton and DeKalb Counties, then connects those outcomes to education and socioeconomic vulnerability. The analysis then shifts to CVS/Aetna's opportunity by comparing known Aetna Medicare Advantage enrollment against the age 65+ population and estimating potential incremental revenue under scenario-based capture assumptions.

## Method Notes

- NCHS is kept separate from Georgia and OASIS because its categories are not directly comparable.
- Age 65+ population is used as a proxy for Medicare-age market opportunity.
- Forecast outputs use analyst assumptions, not CVS-reported projections.
- Interactive charts are generated separately in the `outputs/html` folder.

## Top Mortality Patterns

| Source   | Geography   | Cause                                                                      |   Deaths |
|:---------|:------------|:---------------------------------------------------------------------------|---------:|
| NCHS     | Fulton      | Malignant Neoplasms                                                        |     1409 |
| NCHS     | Fulton      | Diseases of Heart                                                          |     1369 |
| NCHS     | DeKalb      | Malignant Neoplasms                                                        |     1086 |
| NCHS     | DeKalb      | Diseases of Heart                                                          |     1070 |
| Georgia  | Fulton      | Ischemic Heart and Vascular Disease                                        |      492 |
| NCHS     | Fulton      | Unintentional Injuries                                                     |      480 |
| Georgia  | Fulton      | Essential (Primary) Hypertension and Hypertensive Renal, and Heart Disease |      456 |
| Georgia  | Fulton      | All Other Diseases of the Nervous System                                   |      455 |
| OASIS    | Fulton      | All other Diseases of the Nervous System                                   |      455 |
| OASIS    | Fulton      | Obstructive Heart Disease (incl. Heart Attack)                             |      428 |
| Georgia  | Fulton      | Cerebrovascular Disease                                                    |      399 |
| Georgia  | DeKalb      | Ischemic Heart and Vascular Disease                                        |      399 |
| NCHS     | Fulton      | Cerebrovascular Diseases                                                   |      399 |
| OASIS    | Fulton      | Stroke                                                                     |      399 |
| NCHS     | DeKalb      | Unintentional Injuries                                                     |      369 |

## Social Determinants Patterns

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

## Aetna Enrollment

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

## Potential Aetna Market Opportunity

| County   |   Capture Rate |   Potential Members |   Revenue Per Member Assumption |   Incremental Revenue |   Incremental Revenue Millions |
|:---------|---------------:|--------------------:|--------------------------------:|----------------------:|-------------------------------:|
| DEKALB   |           0.01 |             1060.33 |                            5391 |           5.71624e+06 |                        5.71624 |
| DEKALB   |           0.03 |             3180.99 |                            5391 |           1.71487e+07 |                       17.1487  |
| DEKALB   |           0.05 |             5301.65 |                            5391 |           2.85812e+07 |                       28.5812  |
| FULTON   |           0.01 |             1374.15 |                            5391 |           7.40804e+06 |                        7.40804 |
| FULTON   |           0.03 |             4122.45 |                            5391 |           2.22241e+07 |                       22.2241  |
| FULTON   |           0.05 |             6870.75 |                            5391 |           3.70402e+07 |                       37.0402  |

