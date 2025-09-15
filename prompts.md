My goal is building an open source project that will map as JSON Schema all the input and output of the Gerrit REST API. The API expects to receive and respond with data in JSON format and call them as "JSON Entities". Using the schema as the source of truth, I want to generate 3 versions of it: pydantic models, Python dataclass, and Python typeddicts. Then I want to post in PyPI the Python package(s) for people to install and use those versions for type hinting. I also want to support multiple official Gerrit versions: 3.12, 3.11, 3.10... In the schemas and in the Python packages. How would you recommend me to layout this project? How to generate the Python code from the JSON schema?

yes, please generate the schema for all the gerrit API JSON entities. Please use the official documentation from https://gerrit-review.googlesource.com/Documentation/rest-api.html and separate it in JSON file following the same categorization as in the documentation: access.json, accounts.json, changes.json... Also for the description field, use the exact same descriptions as in the documentation


I'll continue working on updating all the schema references to ensure proper cross-linking between entities.

All JSON schema files now have consistent and proper references to related schemas, which will ensure proper validation and type information throughout the codebase.
