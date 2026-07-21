*** Settings ***
Documentation    Verifies that the Robot Framework workspace is executable.

*** Test Cases ***
Robot Framework Is Available
    Should Be Equal    ${TRUE}    ${TRUE}

