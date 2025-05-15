A simple GitHub Action to enforce CRLF on selected file types in your repo.

## Example worflow:

`Path: /.github/workflows/enforce-crlf.yml`
```yml
name: Force CRLF for files inside the Git index

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
      uses: DecimalTurn/Enforce-CRLF@ec751ecfeb0e0cf51d19f295435c7a6ec10bac15 #v1.1.3
      with:
        extensions: .bas, .frm, .cls
        do-checkout: true
        do-push: true
```

Note that in the above example, we are setting `do-checkout` and `do-push` in order to let Enforce-CRLF perform those steps for us. If however, you want Enforce-CRLF to be part of a more complex workflow where you've already performed the `git checkout` and/or will perform the `git push` at the end, you can always set those values to false.

```yml
        do-checkout: false
        do-push: false
```
