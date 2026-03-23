# Quick start

## Step 1: Start the gateway (the engine)

Run this in its own terminal window and leave it open:

```bash
openclaw --profile dev gateway
```

**Why?** This starts the background service, connects your Gemini 3 Flash model, and activates your Discord and Telegram bots.

## Step 2: Run the scout (the mission)

Open a new tab (Cmd + T) in Terminal and run:

```bash
openclaw --profile dev agent --agent main --session-id scout-test-01 -m "Use the firecrawl-scraper tool on 'https://github.com/anthropics/anthropic-cookbook'. Extract technical concepts to 1_scouted_courses/validated/anthropic_concepts.md"
```
