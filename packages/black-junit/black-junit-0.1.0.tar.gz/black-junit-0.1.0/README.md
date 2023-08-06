# black-junit
Module to generate JUnit report from black results

# Usage

pip install .
black . --diff 2>result.txt && cat result.txt | python3 -m black_junit