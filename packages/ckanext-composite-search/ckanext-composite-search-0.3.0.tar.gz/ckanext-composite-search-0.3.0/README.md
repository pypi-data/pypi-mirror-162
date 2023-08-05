[![Tests](https://github.com/DataShades/ckanext-composite-search/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-composite-search/actions)

# ckanext-composite-search

**TODO:** Put a description of your extension here:  What does it do? What features does it have? Consider including some screenshots or embedding a video!


## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible? |
|-----------------|-------------|
| 2.8 and earlier | no          |
| 2.9             | yes         |
|                 |             |


## Installation

To install ckanext-composite-search:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Install the extension

	pip install ckanext-composite-search

3. Add `composite_search default_composite_search` to the `ckan.plugins`
   setting in your CKAN config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

None at present

**TODO:** Document any optional config settings here. For example:

	# The minimum number of hours to wait before re-checking a resource
	# (optional, default: 24).
	ckanext.composite_search.some_setting = some_default_value

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
