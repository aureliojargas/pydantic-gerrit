My goal is building an open source project that will map as JSON Schema all the input and output of the Gerrit REST API. The API expects to receive and respond with data in JSON format and call them as "JSON Entities". Using the schema as the source of truth, I want to generate 3 versions of it: pydantic models, Python dataclass, and Python typeddicts. Then I want to post in PyPI the Python package(s) for people to install and use those versions for type hinting. I also want to support multiple official Gerrit versions: 3.12, 3.11, 3.10... In the schemas and in the Python packages. How would you recommend me to layout this project? How to generate the Python code from the JSON schema?

yes, please generate the schema for all the gerrit API JSON entities. Please use the official documentation from https://gerrit-review.googlesource.com/Documentation/rest-api.html and separate it in JSON file following the same categorization as in the documentation: access.json, accounts.json, changes.json... Also for the description field, use the exact same descriptions as in the documentation


I'll continue working on updating all the schema references to ensure proper cross-linking between entities.

All JSON schema files now have consistent and proper references to related schemas, which will ensure proper validation and type information throughout the codebase.


## Tests

Now I want to focus on the tests. Please ignore the current contents for the tests directory. I want to have a new thing from scratch.

My idea is having local JSON files that represent both input and output from the Gerrit API, so I can test my Python models against it.

We can start by generating those JSON files based in the Gerrit API official documentation, but later I would like to run Gerrit locally (with Docker) and make sure the JSON files are actually correct.

I want to support multiple Gerrit versions, so I need a full set of JSON files for version 3.10, 3.11, 3.12, ...

Do you think this is a good strategy? Which file layout would you recommend? I want to use pytest for testing.



Just to be clear: I don't want to test the Gerrit API. I have mapped the API entities (input and output) as JSON schema in the schemas directory, and I have generated Python code from it in the `generated` directory: pydantic models, dataclasses and typeddicts. I want to test that schemas are correct, and that the generated Python code is correct too. For that I want to have a set of JSON files that represent the input and output of the Gerrit API, so I can validate them against the schemas and also use them to test the generated Python code.

Having a single file test_schemas.py to test all the schemas wouldn't result in a too large file? Currently there's 13 files inside the schemas dir and I think it's still incomplete.

I'm thinking, wouldn't the code in those tests be too repetitive? Like, to test accounts, I guess the only difference is in the way we apply the JSON data (to schema, pydantic, typeddict, dataclass), but all the rest around it would be the same, no?

The code for those validator() methods would be basically the same in all test files, no?

why the "Might need a runtime validator"?

in that case, is it worth to add tests for typeddict?

so without testing typeddicts, we trust the output of the generator blindly, without validating it
