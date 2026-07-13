# Ker Nethalas Digital Companion - Planning Package v0.1

This package contains an initial requirements and data-design pass for a Python 3.12+ computerized companion.

## Included

- `Ker_Nethalas_Digital_Companion_Requirements_v0.1.docx` - product scope, functional requirements, architecture, testing, roadmap, risks, and the Seraphine golden-save scenario.
- `Ker_Nethalas_Data_Model_v0.1.xlsx` - data dictionary, sample static-content tables, Seraphine's paused session, combat snapshot, and regression test cases.
- `ker_nethalas_sample_data_v0.1/` - JSON development samples corresponding to the workbook.

## Recommended first implementation

Build a headless rules engine that loads `seraphine_save.json` and resolves the next Skeletal Horror turn using manually entered dice. Once that works, add the first-Domain exploration state machine, then place a PySide6 interface over the tested engine.

## Important content note

The sample data is intentionally small and paraphrased. It is not a complete transcription of the source rulebook.
