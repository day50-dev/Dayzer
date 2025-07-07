The approach should be agnostic to tooling. Let me make sure this is possible.

The landscape:

- vscode plugins
  - roo, cline, amp, kilo
- ides
  - windsurf, cursor, refact.ai, augment
- cli systems
  - warp, goose, codex, aider, plandex
- dekstop
  - claude, openhands
- chatters
  - llm (simonw), librechat, openwebui, on site chat (web, phone)

1. it looks like the app based ones are islands that can't be violated
2. for the others it might just be tool calling + completions api, tbd


So I guess the goal is to get one flow - two tools to be agnostic. 

Look in the [story](story.md) for more info. Essentially for (2) to be possible, there needs to be a way to do URL overrides


