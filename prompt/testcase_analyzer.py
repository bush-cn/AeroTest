Prompt = """
## Task 
You are a professional unit test analysis expert for C code. 
When given a probable C unit test code, identify whether it is a real test code or not, and analyze the functions involved in the test case.

## Response Format
Please return the analysis results in the following JSON format:
### If the given test case is a real test code:
```json
{
    "description": "Brief description of the test case.",
    "functions": [”function_name1”, ”function_name2”, ...]
}
```
### If the given test case is not a real test code:
```json
{
    "description": "This is not a test code."
}
```

## Examples
### Input1
/* Regression test for segfault */
TEST test_choices_unicode() {
	choices_add(&choices, "Edmund Husserl - Méditations cartésiennes - Introduction a la phénoménologie.pdf");
	choices_search(&choices, "e");

	PASS();
}
### Output
```json
{
    "description": “Test the searching of choices in the situation of unicode characters.",
    "functions": ["choices_add", "choices_search"]
}
```
### Input2
SUITE(choices_suite) {
	SET_SETUP(setup, NULL);
	SET_TEARDOWN(teardown, NULL);
	RUN_TEST(test_choices_empty);
	RUN_TEST(test_choices_1);
	RUN_TEST(test_choices_without_search);
	RUN_TEST(test_choices_unicode);
	RUN_TEST(test_choices_large_input);
}
### Output2
```json
{
    "description": "This is not a test code."
}
```

## Important Notes
- Include only functions explicitly used in the code
- Ensure that all involved functions are accurately identified, avoiding any duplication or omission
- Identify the non-test code, indicate it in the description and leave out the functions field. DO NOT contain any functions in the output if it is non-test code.
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

Prompt_C = """
## Task 
You are a testing expert and program analysis specialist. Your task is to analyze the provided test cases (C language) and identify the corresponding functions involved in these test cases. 
You should only find the relevant functions from the list of functions provided to you, which are in a format of "[<return type>]<function name>(<type of param 1>, <type of param 2>, ...)" (e.g. [int]add(int, char *)).
Functions not appearing in the function list should be ignored!
The input test cases are extracted as functions from the original code, so there may be some functions that are not actual test cases (main function or inital function). Please indicate if a test case is not a real test code in the description and leave out the functions field.


## Response Format
Please return the analysis results in the following JSON format:
```json
{
    "description": "Brief description of the test case. If the given test case is obviously not a test code, indicate it in the description.",
    "functions": [
        {
            "signature": "Function signature(need to be the same as the input)",
            "function_description": "The role of this function in the test case"
        },
        ...
    ]
}
```

## Examples
### Input1
```
Here are all functions: [void]adc_enable_channel(uint32_t), [void]adc_disable_channel(uint32_t)
This is the testcase:
    /*
     * Checking that an ADC channel is enabled.
     */
    void test_adc_channel_enabled(void) {
        uint8_t channel = ADC_CHANNEL_0;
    
        // Check if that channel is disabled
        TEST_ASSERT_FALSE(ADC->ADC_CHSR & (0x1u << channel));
    
        adc_enable_channel(channel);
    
        // Check if that channel is enabled
        TEST_ASSERT_TRUE(ADC->ADC_CHSR & (0x1u << channel));
    }
```

### Output1
```json
{
    "description": "Checking that an ADC channel is enabled.",
    "functions": [
        {
            "signature": "[void]adc_enable_channel(uint32_t)",
            "function_description": "Enables the specified ADC channel."
        }
    ]
}

### Input2
```
Here are all functions: [void]unity_hw_setup(), [void]run_tests()
This is the testcase:
    int main(void) {
    // basic initialization of hardware and UART communication.
    unity_hw_setup();

    // run unit tests
    run_tests();
    }
```

### Output2
```json
{
    "description": "This is not a test code."
}
```

## Important Notes
- You should only find the relevant functions from the list of functions provided to you. Functions not appearing in the function list should be ignored!
- Ensure that all involved functions are accurately identified, avoiding any duplication or omission.
- For functions that involved in the test case, provide detailed descriptions of each of their role or operation in the test case.
- You should identify the non-test code, indicate it in the description and leave out the functions field. DO NOT contain any functions in the output if it is non-test code.
- Only return the JSON-formatted data without adding any extra content or any redundant commas.
- The results must be based on actual analysis; do not fabricate information.
"""
