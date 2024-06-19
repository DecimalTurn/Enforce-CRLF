A simple GitHub Action to enforce CRLF on selected file types in your repo.

Example worflow:
```yml
name: Enforce-CRLF

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

permissions:
  contents: write

jobs:
  enforce-crlf:
    runs-on: ubuntu-latest
    steps:
    - name: Enforce CRLF action
      uses: DecimalTurn/Enforce-CRLF@main
      with:
        extensions: .bas, .frm, .cls
```
