# TODO: 感觉可以不用LLM，直接匹配字符串？LLM的额外作用可能是能提供用例的解释
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
