# Fundamentals-of-Agentic-AI

Assignment 1 is a Next.js web app rather than a uv project. Its README, live URL, and grading evidence are in [assignment-01/README.md](assignment-01/README.md).

One folder per assignment. Each folder is its own uv project with its own
`pyproject.toml` and its own `.venv`, so dependencies never collide.

Run an assignment from inside its folder:

```
cd assignment-01
uv run main.py
```

Start a new assignment by copying the last one:

```
cp -r assignment-01 assignment-02
```

Then edit the `name` in `assignment-02/pyproject.toml`.
