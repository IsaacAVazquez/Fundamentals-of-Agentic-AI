# Fundamentals of Agentic AI

Coursework for Fundamentals of Agentic AI at Berkeley, one folder per assignment.

Course materials pulled from bCourses and the course site, meaning the syllabus, orientation, all seven class decks, the weekly schedule, and the assignment list, are indexed in [COURSE.md](COURSE.md).

| Assignment | What it is | Where |
| --- | --- | --- |
| 1 | Secure networking tracker on Next.js, Neon Postgres, managed Better Auth, and the Neon Data API, live at https://networking-tracker-lyart.vercel.app | [assignment-01/README.md](assignment-01/README.md) has the setup, architecture, schema, security, tests, and grading evidence |
| 2 | Ms. Pac-Man Deep Q-Network from the course notebook, trained on an Apple M4 Pro laptop, first for 500 games and then for 450 after checking every saved checkpoint on games the notebook never plays | [assignment-02/README.md](assignment-02/README.md) has the settings, both runs' scores, the gameplay GIFs and training plots, and the explanation |
| 3 | Word-token nanoGPT from the course notebook, trained twice on a laptop CPU, once on the classroom corpus and once with four generated teaching files for grammar, opposites, negation, and reference, scored on the course's 48 fixed language evals before and after each run, with an optional third run at twice the steps | [assignment-03/README.md](assignment-03/README.md) has the settings, all the eval result sets, the traced token, embedding, gradient, and update, the chat transcripts, and the explanation |

Each assignment folder is self-contained with its own dependencies and its own README, so the README inside the folder is the place to start. Each one also has an `EXPLAINER.md`, which is a plain-language walkthrough of what the code in that folder is doing, written for someone reading it without a background in the stack it uses.
