# Harness Repository

A community-maintained registry of harnesses for the [VS Code Harness Manager](https://marketplace.visualstudio.com/items?itemName=AdmiralGallade.vscode-harness-manager) extension.

Harnesses are pre-built project setups — hooks, skills, rules, and config — that you can install into any project in one click through the extension.

## Available Harnesses

| Name | Category | Description |
|------|----------|-------------|
| Data Intensive | data | Caching, batch processing, and monitoring for data-heavy projects |
| Dev Wiki | knowledge | Project lifecycle system with hooks and companions for Claude Code |
| Knowledge Wiki | knowledge | CRUD operations for persistent knowledge bases |
| Migration | migration | Validation tools and data conversion utilities for system transitions |

Browse the [`harnesses/`](./harnesses/) folder to explore each one.

## Contributing a Harness

Want to share a harness with the community? Raise a pull request — contributions are welcome.

**1. Create a folder under `harnesses/`**

```
harnesses/your-harness-name/
├── README.md          # What this harness does and how to use it
├── LICENSE            # License for your harness
├── hooks/             # Claude Code hooks (optional)
├── rules/             # Rules files (optional)
└── skills/            # Skills (optional)
```

**2. Add an entry to `harnesses.json`**

```json
{
  "id": "your-harness-name",
  "name": "Your Harness Name",
  "description": "One sentence on what this harness does.",
  "category": "data | migration | workflow | knowledge",
  "tags": ["tag1", "tag2"],
  "author": "your-github-username",
  "version": "1.0.0",
  "files": [
    { "path": "harnesses/your-harness-name/README.md", "type": "documentation" }
  ]
}
```

**3. Open a pull request**

Title your PR `feat: add <harness-name> harness` and briefly describe what it does in the body.

## Guidelines

- Include a `README.md` inside your harness folder explaining what it does and any setup steps.
- If your harness is based on someone else's work, include a `LICENSE` file and credit the original source with an attribution block at the top of your `README.md`:

  > **Attribution:** Sourced from [owner/repo](https://github.com/owner/repo) by [@owner](https://github.com/owner), used under the MIT License.

- Keep harnesses focused — one clear purpose per harness.

## License

This repository is licensed under the [MIT License](./LICENSE).
