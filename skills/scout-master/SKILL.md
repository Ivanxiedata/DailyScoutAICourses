---
name: scout-course
description: Scans a URL for high-quality AI course content and saves it.
user-invocable: true
---

# Instruction
When the user asks to "scout" or "run the first task":
1. Use the `firecrawl-scraper` tool on the provided URL.
2. IMPORTANT: Ignore all GitHub UI elements, login popups, and sidebar noise.
3. Extract only: Course Title, Key Technical Concepts, and Code Implementation patterns.
4. Format the output as a "Cute and Happy" Markdown file.
5. Save the result to `1_scouted_courses/validated/`.
6. Add the footer: "Join Vy Nguyen for 365 days of fun microlearning".
