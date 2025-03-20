import json

if __name__ == '__main__':
    try:
        resp = json.loads("""
        {
            "description": "Checking that an ADC channel is enabled.",
            "functions": [
                {
                    "signature": "[void]adc_enable_channel(uint32_t)",
                    "function_description": "Enables the specified ADC channel."
                }
            ]
        }""")
    except Exception as e:
        print(f'Error while extract json from LLM raw output: {e}')
