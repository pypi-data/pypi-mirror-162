# History

0.0.17 (2022-08-10)
-------------------

- Made bumping arrow (dependency) possible.

- Increase timeout for leakge/rain/sources_sinks file upload 'processed' event.


0.0.16 (2022-02-08)
-------------------

- Replaced PyPi token


0.0.15 (2022-02-08)
-------------------

- Bugfix: Don't set `None`` values on threedi-api-client OpenAPI models.


0.0.14 (2021-08-11)
-------------------

- Bugfix in groundwater initial waterlevel scenario handling.

- File structure  control scenario support


0.0.13 (2021-08-03)
-------------------

- Upgraded from `openapi_client` to `threed_api_client`


0.0.12 (2021-08-02)
-------------------

- Added support for schematisations scenarios


0.0.11 (2021-06-15)
-------------------

- Changed import paths


0.0.10 (2021-06-15)
-------------------

- Removed unused imports


0.0.9 (2021-05-05)
------------------

- Renamed general settings to physical settings


0.0.8 (2021-04-28)
------------------

- Use auth refresh method from upstream package.


0.0.7 (2021-04-14)
------------------

- Added settings to scenario-test-framework


0.0.6 (2021-03-24)
------------------

- Added leakage and bumped threedi-openapi-client


0.0.5 (2021-02-05)
------------------

- Specify arrow version, as newer versions don't work well with 'days' directive in
  YAML (arrow is used in jinja2-time).

- Caches the config per endpoint. This includes a scenario folder option to supply
  a custom scenario folder location (per endpoint).


0.0.4 (2021-02-04)
------------------

- Fixed saving 'organisation_uuid' and 'result_folder' with the `api settings`
  command.

- First official release candidate as a typer app that introduces a plugin system.



0.0.3 (2020-12-21)

- Fixed settings context if config file is not yet available.


## 0.0.1b (2020-12-18)

- First (beta) pypi release.
