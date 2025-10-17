# Contributing to MMRRC Ingest

:+1: First of all: Thank you for taking the time to contribute!

The following is a set of guidelines for contributing to
MMRRC Ingest. These guidelines are not strict rules.
Use your best judgment, and feel free to propose changes to this document
in a pull request.

## Table Of Contents

* [Code of Conduct](#code-of-conduct)
* [Guidelines for Contributions and Requests](#contributions)
  * [Reporting issues and making requests](#reporting-issues)
  * [Questions and Discussion](#questions-and-discussion)
  * [Adding new features yourself](#adding-features)
* [Best Practices](#best-practices)
  * [How to write a great issue](#great-issues)
  * [How to create a great pull/merge request](#great-pulls)

<a id="code-of-conduct"></a>

## Code of Conduct

The MMRRC Ingest team strives to create a
welcoming environment for editors, users and other contributors.
Please carefully read our [Code of Conduct](CODE_OF_CONDUCT.md).

<a id="contributions"></a>

## Guidelines for Contributions and Requests

<a id="reporting-issues"></a>

### Reporting problems and suggesting changes to the data ingest

Please use our [Issue Tracker][issues] for any of the following:

- Reporting problems with data transformations
- Requesting new data sources
- Suggesting improvements to the ingest pipeline

<a id="questions-and-discussions"></a>

### Questions and Discussions

Please use our [Discussions forum][discussions] to ask general questions or contribute to discussions about the data ingest process.

<a id="adding-features"></a>

### Adding new features yourself

Please submit a [Pull Request][pulls] to submit improvements to the ingest pipeline.

<a id="best-practices"></a>

## Best Practices

<a id="great-issues"></a>

### GitHub Best Practice

- Creating and curating issues
    - Read ["About Issues"][about-issues]
    - Issues should be focused and actionable
    - Complex issues should be broken down into simpler issues where possible
- Pull Requests
    - Read ["About Pull Requests"][about-pulls]
    - Pull Requests (PRs) should be atomic and aim to close a single issue
    - Long running PRs should be avoided where possible
    - PRs should reference issues following standard conventions (e.g. "fixes #123")
    - Always work on a feature branch, never directly on main
    - PRs should be reviewed and merged in a timely fashion
    - PRs that do not pass GitHub actions should never be merged

### Data Ingest Best Practices

- **Configuration Management**
    - Keep `download.yaml`, `transform.yaml`, and `metadata.yaml` files properly formatted
    - Validate YAML syntax before committing changes
    - Document all configuration parameters
- **Transform Code**
    - Follow Python best practices in `transform.py`
    - Add appropriate error handling and logging
    - Write unit tests for transform logic
- **Data Quality**
    - Validate output data against expected schema
    - Include data quality checks in transforms
    - Document any data cleaning or filtering applied
- **Dependencies**
    - Keep dependencies up to date
    - Only add necessary dependencies
    - Use version pinning for reproducibility

### Understanding Koza

Contributors should familiarize themselves with:

- [Koza Documentation](https://koza.monarchinitiative.org)
- [KGX Documentation](https://github.com/biolink/kgx)
- [Biolink Model](https://biolink.github.io/biolink-model/)

[about-issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues
[about-pulls]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
[issues]: https://github.com/monarch-initiative/mmrrc-ingest/issues/
[pulls]: https://github.com/monarch-initiative/mmrrc-ingest/pulls/
[discussions]: https://github.com/monarch-initiative/mmrrc-ingest/discussions/