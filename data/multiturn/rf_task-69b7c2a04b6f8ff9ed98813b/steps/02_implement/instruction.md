You're working in a C repository at `/opt/netdata.git`.

**Read `/tmp/plan.md` first** - it is the plan you agreed with the maintainer in the previous step. Carry it out now in `/opt/netdata.git`.

- Make the minimal changes to **non-test source files only**. Do **NOT** modify any test files or testing logic in any way - the maintainer has already handled the tests.
- Keep the project building and the existing behavior intact as you refactor.
- Before editing, configure a local git identity if this repo does not already have one:

```bash
git config user.name "Dev"
git config user.email "dev@example.com"
```

- Save the starting commit before your first implementation commit:

```bash
git rev-parse HEAD > /tmp/base_commit.txt
```

- After each coherent implementation pass, commit the current repo changes before asking the maintainer for review. A coherent pass is the initial implementation, or a later revision made in response to maintainer feedback. Use short commit messages like `initial implementation` or `address feedback: metrics`.
- The maintainer can inspect the repository state directly after your commit, so a concise review request is fine. Still make sure each coherent implementation pass is committed before calling `ask_user`.
- Do not commit `/logs`, temporary investigation files, or unrelated generated files.
- When you believe it is done, run focused validation if practical, review the latest commit and working tree, then report the key changes to the maintainer via `ask_user`. If they ask for changes, make another coherent pass and commit it. If they say ship it, then finish.
