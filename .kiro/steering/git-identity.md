# Git identity for agent commits

- Commits made by the agent use the bot identity as both author and committer, passed per commit (do not change git config):
  `GIT_COMMITTER_NAME="m1k3png" GIT_COMMITTER_EMAIL="350223567+m1k3png@users.noreply.github.com" git commit --author="m1k3png <350223567+m1k3png@users.noreply.github.com>" -m "..."`
- Work on a feature branch and open a pull request; never push directly to `main`.
- Don't add `Co-Authored-By` trailers to commit messages.
- Keep credits to upstream authors (Vikey by Tony Dinh, OpenKey by Tuyen Mai) in README/About as GPL-3.0 requires.
