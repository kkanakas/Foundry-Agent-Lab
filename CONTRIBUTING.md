# Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## How to Contribute

1. **Fork** the repository and create a feature branch from `main`.
2. **Follow the existing structure** — each demo is self-contained with its own `create_agent.py`, `chat.py`, `demo.bat`, `reset.bat`, and documentation files.
3. **Test your changes** end-to-end with `az login` and a real Foundry project before submitting.
4. **Do not commit** `.env` files or any files containing credentials or personal endpoint URLs.
5. **Submit a pull request** with a clear description of what the change does and why.

## Reporting Issues

Use [GitHub Issues](../../issues) to report bugs or request features. Please include:
- The demo folder that exhibits the problem
- Steps to reproduce
- Expected vs. actual behaviour
- Any relevant error output
