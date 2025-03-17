(function_invocation
  (identifier) @function.invocation.identifier
  (#eq? @function.invocation.identifier "ClassName")
) @function.invocation

(field_access
    (identifier) @field.access.identifier
    (#eq? @field.access.identifier "FieldAccessName")
) @field.access
