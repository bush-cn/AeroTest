Prompt_C = """
## Task 
You are a testing expert and program analysis specialist. Your task is to analyze the provided test cases (C language) and identify the corresponding structs and functions involved in these test cases. 
You should only find the relevant structs from the list of structs provided to you. 

## Response Format
Please return the analysis results in the following JSON format:
```json
{
    "test_case_name": "Name of the test case(need to be the same as the original code)",
    "description": "Brief description of the test case",
    "classes": [
        {
            "class_name": "Class name",
            "class_description": "The role or function of this class in the test case",
            "methods": [
                {
                    "method_name": "Method name",
                    "method_description": "The role or operation of this method in the test case"
                },
                ...
            ]
        },
        ...
    ],
    "independent_methods": [
        {
            "method_name": "Method name",
            "method_description": "The role or operation of this method in the test case"
        },
        ...
    ]
}
```

## Examples
### Input
```
Here are all class: AAABBB, Application, UserRestClient, UserController, RunNotFoundException, RunController, JdbcRunRepository, RunJsonDataLoader, InMemoryRunRepository.
This is the testcase:
    def test_update_run(self):
        s = Solution()
        repository.update(Run(1,
                "Monday Morning Run",
                datetime.now(),
                datetime.now() + timedelta(minutes=30),
                5,
                Location.OUTDOOR), 1)
        s.assertEqual("Monday Morning Run", repository.find_by_id(1).title)
        run = repository.find_by_id(1)
        self.assertEqual("Monday Morning Run", run.title)
        self.assertEqual(5, run.miles)
        self.assertEqual(Location.OUTDOOR, run.location)
These are all the references in the same file that are involved in the test case:[{'repository': 'JdbcRunRepository'}]
```

### Output
```json
{
    "test_case_name": "test_update_run",
    "description": "Tests the functionality of updating a run in the repository and verifying the updated details.",
    "classes": [
        {
            "class_name": "JdbcRunRepository",
            "class_description": "Class responsible for managing the persistence of Run objects using JDBC.",
            "methods": [
                {
                    "method_name": "update",
                    "method_description": "Updates an existing Run object in the repository."
                },
                {
                    "method_name": "find_by_id",
                    "method_description": "Retrieves a Run object from the repository by its ID."
                }
            ]
        }
    ],
    "independent_methods": []
}
```
### Explanation
The testcase `test_update_run` contains several classes, but only the `repository`, which is of type `JdbcRunRepository`, appears in the provided class list. 
Therefore, only the `JdbcRunRepository` class is returned.

## Important Notes
- You should only find the relevant classes from the list of classes provided to you. Classes not appearing in the class list should be ignored!
- Ensure that all involved classes and methods are accurately identified, avoiding any duplication or omission.
- For methods that belong to a class, provide detailed descriptions of each class and method's role or operation in the test case.
- For independent methods that do not belong to any class, also provide detailed descriptions of their roles in the test case.
- Only return the JSON-formatted data without adding any extra content.
- The results must be based on actual analysis; do not fabricate information.
"""

Prompt_Java = """
## Task
You are a testing expert and program analysis specialist. Your task is to analyze the provided test cases and identify the corresponding classes and methods involved in these test cases. 
You should only find the relevant classes from the list of classes provided to you. Classes not appearing in the class list should be ignored!

## Response Format
Please return the analysis results in the following JSON format:
```json
{
    "test_case_name": "Name of the test case(need to be the same as the original code)",
    "description": "Brief description of the test case",
    "classes": [
        {
            "class_name": "Class name",
            "class_description": "The role or function of this class in the test case",
            "methods": [
                {
                    "method_name": "Method name",
                    "method_description": "The role or operation of this method in the test case"
                },
                ...
            ]
        },
        ...
    ],
    "independent_methods": [
        {
            "method_name": "Method name",
            "method_description": "The role or operation of this method in the test case"
        },
        ...
    ]
}
```

## Examples
### Input
```
Here are all class: AAABBB, Application, UserRestClient, UserController, RunNotFoundException, RunController, JdbcRunRepository, RunJsonDataLoader, InMemoryRunRepository.
This is the testcase:
    @Test
    void shouldUpdateRun() {
        repository.update(new Run(1,
                "Monday Morning Run",
                LocalDateTime.now(),
                LocalDateTime.now().plus(30, ChronoUnit.MINUTES),
                5,
                Location.OUTDOOR), 1);
        var run = repository.findById(1).get();
        assertEquals("Monday Morning Run", run.title());
        assertEquals(5, run.miles());
        assertEquals(Location.OUTDOOR, run.location());
    }
These are all the references in the same file that are involved in the test case:[{'repository': 'JdbcRunRepository'}]
The following are all the definitions of the referenced record:[{'Run': [{'name': 'id', 'type': 'Integer'}, {'name': 'title', 'type': 'String'}, {'name': 'startedOn', 'type': 'LocalDateTime'}, {'name': 'completedOn', 'type': 'LocalDateTime'}, {'name': 'miles', 'type': 'Integer'}, {'name': 'location', 'type': 'Location'}]}]
```
### Output
```json
{
    "test_case_name": "shouldUpdateRun",
    "description": "Tests the functionality of updating a run in the repository and verifying the updated details.",
    "classes": [
        {
            "class_name": "JdbcRunRepository",
            "class_description": "Class responsible for managing the persistence of Run objects using JDBC.",
            "methods": [
                {
                    "method_name": "update",
                    "method_description": "Updates an existing Run object in the repository."
                },
                {
                    "method_name": "findById",
                    "method_description": "Retrieves a Run object from the repository by its ID."
                }
            ]
        }
    ],
    "independent_methods": []
}
```
### Explanation
The testcase `shouldUpdateRun` contains several classes, but only the `repository`, which is of type `JdbcRunRepository`, appears in the provided class list. 
Therefore, only the `JdbcRunRepository` class is returned.

## Important Notes
- You should only find the relevant classes from the list of classes provided to you. Classes not appearing in the class list should be ignored!
- Ensure that all involved classes and methods are accurately identified, avoiding any duplication or omission.
- For methods that belong to a class, provide detailed descriptions of each class and method's role or operation in the test case.
- For independent methods that do not belong to any class, also provide detailed descriptions of their roles in the test case.
- Only return the JSON-formatted data without adding any extra content.
- The results must be based on actual analysis; do not fabricate information.
"""