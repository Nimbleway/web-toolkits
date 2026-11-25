# Nimble Web Toolkits

Grouped agent skills that give your AI agent (Claude, ChatGPT, Cursor, Codex and others) the live web as cited, structured data, powered by [Nimble](https://www.nimbleway.com). Each toolkit installs as one plugin with its skills and the Nimble MCP server bundled.

| Toolkit | For | Skills |
| - | - | - |
| [GTM Web Toolkit](gtm-web-toolkit/) | Sales, SDR, RevOps and marketing teams | Onboarding, account deep research (12 GTM Web Search Agents), account fast search (with `company` and `creators` focus modes), people research, account lists and CRM enrichment, GTM data at scale |
| [Hedge Fund Web Toolkit](hedge-fund-web-toolkit/) | Analysts, PMs, credit and event-driven desks | Onboarding, company deep research (13 hedge fund Web Search Agents), company fast search, filings, media and PDFs, alt data at scale |

## Install

Get a free trial first: https://online.nimbleway.com/signup

**Claude Code, with the MCP server bundled:**

```bash
claude plugin marketplace add Nimbleway/web-toolkits
```

```bash
claude plugin install gtm-web-toolkit@web-toolkits
```

```bash
claude plugin install hedge-fund-web-toolkit@web-toolkits
```

**Claude Code, Codex, Cursor and other agents:**

```bash
npx skills add https://github.com/Nimbleway/web-toolkits/tree/main/gtm-web-toolkit
```

```bash
npx skills add https://github.com/Nimbleway/web-toolkits/tree/main/hedge-fund-web-toolkit
```

Each toolkit's README covers ChatGPT, Claude.ai and other hosts, how to connect Nimble, and its benchmark.

## License

MIT. See [LICENSE](LICENSE).
