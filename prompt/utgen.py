Prompt = """
Please generate unit test code for the following C++ code with a focus on memory safety issues. The tests should specifically target potential problems like:
1. **Null Pointer Dereferencing**: Ensure there are no cases where a null pointer is dereferenced, leading to undefined behavior.
2. **Memory Leaks**: Check that all allocated memory is properly deallocated (using delete, delete[], or smart pointers like std::unique_ptr or std::shared_ptr), and there are no memory leaks.
3. **Dangling Pointers**: Ensure there are no references to freed or deleted memory, which could cause crashes or undefined behavior.
4. **Buffer Overflows**: Ensure no buffer overflows occur by accessing arrays or buffers beyond their allocated bounds.
5. **Resource Management**: Ensure proper management of resources, especially with dynamic memory allocation, file handles, and other non-memory resources.
6. **Uninitialized Pointers/Variables**: Ensure no uninitialized pointers or variables are used, as this can lead to undefined behavior.

Also, ensure that the tests cover the following scenarios:
1. **Normal Input**: Regular valid inputs.
2. **Boundary Conditions**: Edge values and limits.
3. **Invalid Input**: Invalid parameters or exceptional cases.
4. **Edge Cases**: Rare inputs or cases that might trigger memory safety issues.

Additionally, only response the test code **without code block formatting** and do NOT include any other content.
Here is the given C++ code:
"""