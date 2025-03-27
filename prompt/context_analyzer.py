Prompt = """
## Task 
You are a professional static analysis expert for C code. When given a C function, generate a JSON specification of required testing dependencies.
Specifically, analyze the input function to identify:
- Directly called functions (both standard library and user-defined)
- User Defined Types (UDTs: structs, enums, unions) used in parameters, returns, or variables
- Global variables accessed (both read and write operations)
- Macro definitions required for compilation

## Response Format
Please return the analysis results in the following JSON format:
```json
{
    "functions": [”function_name1”, ”function_name2”, ...],
    "udts": [”udt_name1”, ”udt_name2”, ...],
    "global_variables": [”variable_name1”, ”variable_name2”, ...],
    "macros": [”macro_name1”, ”macro_name2”, ...]
}
```

## Examples
### Input
void choices_init(struct choices *c, options_t *options) {
    c->strings = NULL;
    c->results = NULL;

    c->buffer_size = buffer_size;
    c->buffer = NULL;

    c->capacity = c->size = 0;
    choices_resize(c, INITIAL_CHOICE_CAPACITY);

    if (options->workers) {
        c->worker_count = options->workers;
    } else {
        c->worker_count = (int)sysconf(_SC_NPROCESSORS_ONLN);
    }

    choices_reset_search(c);
}
### Output
```json
{
    "functions": ["choices_resize", "choices_reset_search", "sysconf"],
    "udts": ["struct choices", "options_t"],
    "global_variables": ["buffer_size"],
    "macros": ["INITIAL_CHOICE_CAPACITY", "_SC_NPROCESSORS_ONLN"]
}
```

## Important Notes
- Include only types/functions explicitly used in the code
- Preserve exact type declarations including struct/enum/union keywords
- Ensure that all dependencies are accurately identified, avoiding any duplication or omission
- Only return the JSON-formatted data without adding any extra content
- The results must be based on actual analysis; do not fabricate information.
"""

Prompt_v1 = """
## Task 
You are a source code analysis specialist. Your task is to analyze the provided function code (C language) and identify the corresponding functions and structs involved in these code. 
You should only find the relevant functions and structs from the list provided to you.
The given functions are in a format of "[<return type>]<function name>(<type of param 1>, <type of param 2>, ...)" (e.g. [int]add(int, char *)), while the structs are in a format of "struct <struct name>" or "<typedef name>".
Functions and structs not appearing in the list should be ignored!

## Response Format
Please return the analysis results in the following JSON format:
```json
{
    "description": "Brief description of the function.",
    "related_functions": [
        {
            "signature": "Function signature(need to be the same as the input)",
            "function_description": "The role of this function in the test case",
        },
        ...
    ],
    "related_structs": [
        "Struct Name(need to be the same as the input)",
        ...
    ]
}
```

## Examples
### Input
```
Here are all functions: [void]choices_resize(choices_t *, size_t), [void]choices_reset_search(choices_t *).
Here are all structs: choices_t, options_t, struct scored_result, pthread_t.
This is the function code:
    void choices_init(choices_t *c, options_t *options) {
        c->strings = NULL;
        c->results = NULL;

        c->buffer_size = 0;
        c->buffer = NULL;

        c->capacity = c->size = 0;
        choices_resize(c, INITIAL_CHOICE_CAPACITY);

        if (options->workers) {
            c->worker_count = options->workers;
        } else {
            c->worker_count = (int)sysconf(_SC_NPROCESSORS_ONLN);
        }

        choices_reset_search(c);
    }
```

### Output
```json
{
    "description": "Initializes the choices_t structure.",
    "related_functions": [
        {
            "signature": "[void]choices_resize(choices_t *, size_t)",
            "function_description": "Resizes the choices_t structure to the specified size."
        },
        {
            "signature": "[void]choices_reset_search(choices_t *)",
            "function_description": "Resets the search in the choices_t structure."
        }
    ],
    "related_structs": [
        "choices_t",
        "options_t"
    ]
}

### Explanation
The function `choices_init` calls several functions, but only "choices_resize" and "choices_reset_search" are provided in the list of functions. It also calls the function "sysconf" which is not included in the list, so it should be ignored.
Meanwhile, the function uses structs "choices_t" and "options_t" but doesn't use the given structs "struct scored_result" and "pthread_t", which should not be included in the output.

## Important Notes
- You should only find the relevant functions and structs from the list provided to you. Functions and structs not appearing in the list should be ignored!
- Ensure that all involved functions and structs are accurately identified, avoiding any duplication or omission.
- For functions that involved in the function, provide detailed descriptions of each of their role or operation in the function.
- Only return the JSON-formatted data without adding any extra content or any redundant commas.
- The results must be based on actual analysis; do not fabricate information.
"""