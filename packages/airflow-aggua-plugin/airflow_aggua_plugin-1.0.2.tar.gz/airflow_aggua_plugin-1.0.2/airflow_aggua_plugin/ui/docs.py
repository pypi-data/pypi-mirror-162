"""
Metadata that defines a single API:
{
    "name": "{string}",                     # Name of the API
    "description": "{string}",              # Description of the API
    "http_method": "{string}",              # HTTP method to use when calling the function.
    "form_enctype": "{string}",             # Optional encoding type
    "arguments": [                          # List of arguments that can be provided to the API
        {
            "arg1": "val1",    
        }
    ],
    "post_arguments": [                     # List of arguments that can be provided in the POST body to the API
        {
            "arg1": "val1",
        }
    ]
},
"""

api_metadata = []
