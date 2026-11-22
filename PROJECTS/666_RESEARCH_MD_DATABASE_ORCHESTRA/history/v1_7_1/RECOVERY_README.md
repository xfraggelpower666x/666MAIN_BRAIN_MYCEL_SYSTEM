# Recovery Readme

```bash
unzip 666_RESEARCH_MD_DATABASE_ORCHESTRA_v1_7_1_AUDITED_FREEZE_CLEAN_SYSTEM_ONLY_SYSTEMSICHERUNG_666.zip
cd 666_RESEARCH_MD_DATABASE_ORCHESTRA_v1_7_1_AUDITED_FREEZE_CLEAN_SYSTEM_ONLY
npm test
python3 tools/stem_masking_analyzer.py --self-test
python3 tools/sonification_audio_pipeline.py --self-test
```

`npm run build` creates local generated output for verification. Such output is intentionally not included in this backup.
