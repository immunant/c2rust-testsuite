# c2rust testsuite

# prerequisites

- python 3.6 or later.
- `intercept-build` in path. installing:
    - `pip3 install -r requirements.txt`

# adding new repos

    path/to/repo/$PROJ$ git submodule add --depth 10 -b $BRANCH $PROJ_URL

# TODOs
- [ ] check requirements on ubuntu
- [ ] check requirements on macOS
- [ ] add provision.py driven by `**/dependencies.yml`