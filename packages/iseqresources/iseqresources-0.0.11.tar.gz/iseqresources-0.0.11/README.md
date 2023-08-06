# Iseq resources

Scripts that allow you to:
1) Adding a new tool to the JSON file
2) Iterating over the tools in the JSON file and checking the latest version, and in the case of a new version, adding a tooltip to JIRA
3) Update existing tool/database record in JSON after updating tool/database

## Install

```
pip install iseqresources
```

## Requirements

- python >=3.6
- jira >= 3.3.0
- requests >= 2.22.0
- python-gitlab >= 3.7.0


## Adding a new tool

Input JSON file (`--input-json`) is from gitlab repo at path `json/tools_and_databases.json`

```
add_new_tool
```

You can also run on a local file:

```
add_new_tool \
    --input-json "/path/to/json/tools_and_databases.json"
```

## Checking versions and add task to JIRA

Input JSON file (`--input-json` and `--info-json`) are from gitlab repo at path `json/tools_and_databases.json` and `json/info.json`

```
check_versions
```

You can also run on a local files:

```
check_versions \
    --input-json "/path/to/json/tools_and_databases.json" \
    --info-json "/path/to/json/info.json"
```

## Update existing tool/database record in JSON

Input JSON file (`--input-json`) is from gitlab repo at path `json/tools_and_databases.json`

```
update_record
```

You can also run on a local file:

```
update_record \
    --input-json "/path/to/json/tools_and_databases.json"
```

## What JSON files should look like

1) `--input-json`:

```
[
    {
        "name": "AnnotSV",
        "current_version": "v3.0",
        "newest_version": "",
        "last_check": "",
        "test": "github",
        "repoWithOwner": "lgmgeo/AnnotSV",
        "update_task": [
            "sv_annotsv"
        ]
    },
    {
        "name": "Uniprot",
        "current_version": "2021_03",
        "expected_version": [
            "2021_04",
            "2021_05",
            "2021_06",
            "2022_01",
            "2022_02",
            "2022_03"
        ],
        "newest_version": "",
        "last_check": "",
        "test": "url-check",
        "url": "https://ftp.uniprot.org/pub/databases/uniprot/previous_releases/release-{expected_version}/",
        "update_task": [
            "vcf_acmg_ps3"
        ]
    },
    {
        "name": "Clinvar",
        "current_version": "202206",
        "expected_version": [
            "202207",
            "202208",
            "202209",
            "202210"
        ],
        "release_day": "unknown",
        "newest_version": "",
        "last_check": "",
        "test": "url-check",
        "url": "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar_{expected_version}{wildcard}.vcf.gz.md5",
        "update_task": [
            "vcf_acmg_ps3"
        ]
    },
    {
        "name": "hpo",
        "current_version": "2022/01/13",
        "newest_version": "",
        "update_every_nth_month": 3,
        "test": "update-every-nth-month",
        "url": "https://hpo.jax.org/app/download/annotation and https://hpo.jax.org/app/download/ontology",
        "update_task": [
        "vcf_anno_hpo"
        ]
    }
]
```

2) `--info-json`:

```
{
    "server": "https://test.atlassian.net",
    "epic_id": "TEST-2",
    "project_key": "TEST"
}
```