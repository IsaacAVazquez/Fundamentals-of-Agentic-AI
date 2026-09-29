"""Allow `python -m personal_wiki ...` to run the CLI without installing it."""
from .cli import main

raise SystemExit(main())
