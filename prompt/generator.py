# TODO: 是否可以将头文件中的宏定义、全局变量等信息也加入context？
Prompt_has_ref = """
## Task
You are a test expert for C language. Your task is to generate unit test "Testcase A" for "Code A" according to the test case information "Testcase B" of "Code B" that has some similarity to "Code A".
The confidence of referential relationship between "Code A" and "Code B" will be given together. The closer to 1.0, the higher the similarity between them, and the more possible you can refer to the "Testcase B".

## Input
- "Code A": the function that you need to generate a test case for
- context: the context information of "Code A", including the description of the function, related functions, and related structs
- "Code B": the function that has a similarity to "Code A"
- similarity: the similarity between "Code A" and "Code B" (0.0 <= similarity <= 1.0), or the confidence of referential relationship between "Code A" and "Code B"
- "Testcase B": the test case information of "Code B" that you can refer to

## Output
Your output "Testcase A" must be C code that passes the syntax and can be run successfully.

## Examples
### Input
"Code A":
    void adc_disable_channel(uint32_t channel) {
        if (channel <= ADC_CHANNEL_MAX) {
            ADC->ADC_CHDR = (0x1u << channel);
        }
    }

context:
- description of this function: "Disables the specified ADC channel."
- related functions: []
- related structs: []

"Code B":
    void adc_enable_channel(uint32_t channel) {
        if (channel <= ADC_CHANNEL_MAX) {
            ADC->ADC_CHER = (0x1u << channel);
        }
    }

similarity: 1.0

"Testcase B":
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
    
macros of "Testcase B":
    #include "unity/unity.h"
    #include "test/test_adc.h"
    
### Output
```c
/*
 * Checking that an ADC channel is disabled.
 * Requires "test_adc_channel_enabled"
 * to pass it's test
 */
void test_adc_channel_disabled(void) {
    uint8_t channel = ADC_CHANNEL_0;
    adc_enable_channel(channel);

    // Check if that channel is enabled
    TEST_ASSERT_TRUE(ADC->ADC_CHSR & (0x1u << channel));

    adc_disable_channel(channel);

    // Check if that channel is disabled
    TEST_ASSERT_FALSE(ADC->ADC_CHSR & (0x1u << channel));
}
```


## Important Notes
- Priority in the generated "Testcase A": correctness > coverage > conciseness
- If the similarity is close to 1.0, the generated "Testcase A" should be as similar as possible to "Testcase B" in terms of function name, description, and test logic
- If the similarity is below 0.5, you can ignore the "Testcase B" and generate a new test case based on the context of "Code A"
- The generated result should only contain the test code without adding any extra content.
- If the correlation information is insufficient, please generate basic test cases to ensure that the code path is reasonably covered
"""
