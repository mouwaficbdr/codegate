import subprocess
import os
import json
import tempfile
import shutil

class CodeRunner:
    def __init__(self):
        self.timeout = 3  # Seconds

    def run_tests(self, user_code, func_name, tests, language="python", types=None):
        """
        Runs the user code against tests and returns a structured result dict.
        Result format:
        {
            "success": bool,       # True if ALL tests passed
            "error": str|None,     # Compilation/Runtime error message
            "results": [           # List of test results
                {
                    "input": ...,
                    "expected": ...,
                    "actual": ...,
                    "passed": bool,
                    "log": str     # Captured stdout during test
                }
            ]
        }
        """
        if language == "python":
            return self._run_python(user_code, func_name, tests)
        elif language == "javascript":
            return self._run_javascript(user_code, func_name, tests)
        elif language == "php":
            return self._run_php(user_code, func_name, tests)
        elif language == "c":
            return self._run_c(user_code, func_name, tests, types)
        else:
            return {"success": False, "error": f"Unsupported language: {language}", "results": []}

    def _run_python(self, user_code, func_name, tests):
        driver_code = f"""
import json
import sys
import traceback

# User Code
{user_code}

# Driver Code
tests = {json.dumps(tests)}
results = []
all_passed = True

for t in tests:
    try:
        input_args = t["input"]
        expected = t["expected"]
        
        # Handle single vs multiple args
        if isinstance(input_args, list):
            actual = {func_name}(*input_args)
        else:
            actual = {func_name}(input_args)
            
        passed = (actual == expected)
        if not passed:
            all_passed = False
            
        results.append({{
            "input": input_args,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "log": ""
        }})
    except Exception:
        all_passed = False
        results.append({{
            "input": t.get("input"),
            "expected": t.get("expected"),
            "actual": "Error",
            "passed": False,
            "log": traceback.format_exc()
        }})

print(json.dumps({{"success": all_passed, "results": results}}))
"""
        try:
            result = subprocess.run(
                ["python3", "-c", driver_code],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                return {"success": False, "error": result.stderr, "results": []}
                
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"success": False, "error": f"Invalid output format: {result.stdout}", "results": []}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution Timed Out", "results": []}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def _run_javascript(self, user_code, func_name, tests):
        # Node.js Driver
        driver_code = f"""
{user_code}

const tests = {json.dumps(tests)};
const results = [];
let allPassed = true;

function run() {{
    for (const t of tests) {{
        try {{
            let inputArgs = t.input;
            let expected = t.expected;
            let actual;
            
            if (Array.isArray(inputArgs)) {{
                actual = {func_name}(...inputArgs);
            }} else {{
                actual = {func_name}(inputArgs);
            }}
            
            // Deep equality check for arrays/objects
            let passed = JSON.stringify(actual) === JSON.stringify(expected);
            
            if (!passed) allPassed = false;
            
            results.append({{
                "input": inputArgs,
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "log": ""
            }});
        }} catch (e) {{
            allPassed = false;
            results.push({{
                "input": t.input,
                "expected": t.expected,
                "actual": "Error",
                "passed": false,
                "log": e.toString()
            }});
        }}
    }}
    console.log(JSON.stringify({{"success": allPassed, "results": results}}));
}}
run();
"""
        # Fix for JS append vs push
        driver_code = driver_code.replace("results.append", "results.push")

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(driver_code)
                temp_path = f.name

            result = subprocess.run(
                ["node", temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            os.unlink(temp_path)

            if result.returncode != 0:
                return {"success": False, "error": result.stderr, "results": []}

            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"success": False, "error": f"Invalid output: {result.stdout}", "results": []}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution Timed Out", "results": []}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def _run_php(self, user_code, func_name, tests):
        driver_code = f"""
<?php
{user_code}

$tests = json_decode('{json.dumps(tests)}', true);
$results = [];
$allPassed = true;

foreach ($tests as $t) {{
    try {{
        $input = $t['input'];
        $expected = $t['expected'];
        
        if (is_array($input)) {{
            $actual = {func_name}(...$input);
        }} else {{
            $actual = {func_name}($input);
        }}
        
        // Loose equality for simplicity, or strict if needed
        $passed = ($actual == $expected);
        
        if (!$passed) $allPassed = false;
        
        $results[] = [
            "input" => $input,
            "expected" => $expected,
            "actual" => $actual,
            "passed" => $passed,
            "log" => ""
        ];
    }} catch (Exception $e) {{
        $allPassed = false;
        $results[] = [
            "input" => $t['input'],
            "expected" => $t['expected'],
            "actual" => "Error",
            "passed" => false,
            "log" => $e->getMessage()
        ];
    }}
}}

echo json_encode(["success" => $allPassed, "results" => $results]);
?>
"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
                f.write(driver_code)
                temp_path = f.name

            result = subprocess.run(
                ["php", temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            os.unlink(temp_path)

            if result.returncode != 0:
                return {"success": False, "error": result.stderr, "results": []}

            try:
                # PHP might output warnings before JSON, find the JSON part
                output = result.stdout
                json_start = output.find('{')
                if json_start != -1:
                    output = output[json_start:]
                return json.loads(output)
            except json.JSONDecodeError:
                return {"success": False, "error": f"Invalid output: {result.stdout}", "results": []}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution Timed Out", "results": []}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def _run_c(self, user_code, func_name, tests, types):
        if not types:
            return {"success": False, "error": "Missing type definitions for C", "results": []}

        # Construct C Driver
        # We need to serialize inputs/outputs manually or use a simple format
        # For simplicity in this MVP, we'll hardcode the test cases into the C main function
        
        c_driver = f"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// Helpers for JSON output
void print_json_start() {{ printf("{{\\"results\\": ["); }}
void print_json_end(bool success) {{ printf("], \\"success\\": %s}}", success ? "true" : "false"); }}
void print_test_result(bool first, char* input_desc, char* expected_desc, char* actual_desc, bool passed) {{
    if (!first) printf(",");
    printf("{{\\"input\\": \\"%s\\", \\"expected\\": \\"%s\\", \\"actual\\": \\"%s\\", \\"passed\\": %s}}", 
           input_desc, expected_desc, actual_desc, passed ? "true" : "false");
}}

// User Code
{user_code}

int main() {{
    bool all_passed = true;
    print_json_start();
    
    // Tests
"""
        
        for i, test in enumerate(tests):
            # This is a simplified C generator. 
            # Real-world C generation for arbitrary types is complex.
            # We assume basic types (int, char*, int*) based on the 'types' metadata.
            
            args = test['input']
            expected = test['expected']
            
            # Generate C code to call function and check result
            # This part is highly dependent on the specific challenge types
            # For MVP, we will try to support basic int/string cases
            
            # ... (Complex C generation logic would go here) ...
            # For now, let's return a placeholder error if C is used, 
            # or implement a very basic runner for "int -> int" functions
            
            pass # Placeholder for C logic expansion
            
        c_driver += """
    print_json_end(all_passed);
    return 0;
}
"""
        # NOTE: C support is limited in this dynamic generation approach without a heavy transpiler.
        # We will return a "Not Implemented fully" for C in this specific refactor step 
        # unless we implement the full type mapping.
        # Let's stick to a basic implementation that compiles but might fail complex types.
        
        return {"success": False, "error": "C runner dynamic generation is currently limited. Please use Python/JS/PHP for now.", "results": []}
