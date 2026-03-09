# Algorithms

## YAML Patch Algorithm
1. Parse YAML with preserved formatting
2. Resolve nested path segments (`a.b.c`)
3. Capture previous value
4. Apply new value at target path
5. Serialize YAML and generate unified diff

## Key Policy Matching
1. Validate key-path shape using regex
2. Match exact allow-list entries
3. Match wildcard entries (`prefix.*`) for nested keys

## Execution Strategy
- Uses bounded thread pool to process multiple targets concurrently
- Sorts outputs by application for deterministic response ordering
