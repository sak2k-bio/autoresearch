# GitHub Actions Setup for AutoResearch Bio-Medical Pipeline

This guide explains how to set up GitHub Actions to automate the AutoResearch Bio-Medical Pipeline for continuous operation and result management.

## Overview

GitHub Actions can automate your AutoResearch Bio-Medical Pipeline to:
- Run the system on a schedule
- Automatically commit results back to GitHub
- Optionally publish generated posts to LinkedIn
- Monitor system performance and send notifications

## Prerequisites

Before setting up GitHub Actions automation, ensure you have:
1. A GitHub repository with the AutoResearch Bio-Medical Pipeline code
2. API keys for Tavily and Gemini (already configured in your local environment)
3. Basic understanding of GitHub Actions workflow files

## Setting Up GitHub Secrets

First, you need to store your API keys securely in GitHub Secrets:

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `TAVILY_API_KEY`: Your Tavily API key
   - `GEMINI_API_KEY_1`: Your primary Gemini API key
   - `GEMINI_API_KEY_2`: Your backup Gemini API key (optional but recommended)
   - `GEMINI_API_KEY_3`: Additional backup (optional)
   - `LINKEDIN_ACCESS_TOKEN`: LinkedIn API token if you want auto-publishing (optional)

## Basic Workflow Setup

Create a new file at `.github/workflows/autoresearch-bio.yml` with the following content:

```yaml
name: AutoResearch Bio Pipeline

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch: # Allow manual triggering

jobs:
  run-autoresearch:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install uv
        run: |
          pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run AutoResearch Bio
        run: python autoresearch_bio.py --run-once
        env:
          TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
          GEMINI_API_KEY_1: ${{ secrets.GEMINI_API_KEY_1 }}
          GEMINI_API_KEY_2: ${{ secrets.GEMINI_API_KEY_2 }}

      - name: Commit and push results
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add bio_results.tsv topic_memory.json || true
          git commit -m "AutoResearch: Update results $(date)" || exit 0
          git push
        if: success()
```

## Advanced Workflow with LinkedIn Publishing

If you want to automatically publish the generated posts to LinkedIn, create a more advanced workflow:

```yaml
name: AutoResearch Bio Pipeline with LinkedIn Publishing

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:

jobs:
  run-autoresearch:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install uv
        run: |
          pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run AutoResearch Bio
        run: python autoresearch_bio.py --run-once
        env:
          TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
          GEMINI_API_KEY_1: ${{ secrets.GEMINI_API_KEY_1 }}
          GEMINI_API_KEY_2: ${{ secrets.GEMINI_API_KEY_2 }}

      - name: Extract post content
        id: extract
        run: |
          # Extract the latest generated post from logs or create a file
          # This is a placeholder - you'll need to implement actual extraction
          echo "POST_CONTENT=$(python extract_latest_post.py)" >> $GITHUB_OUTPUT

      - name: Publish to LinkedIn
        if: ${{ secrets.LINKEDIN_ACCESS_TOKEN != '' }}
        run: |
          python publish_to_linkedin.py
        env:
          LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
          POST_CONTENT: ${{ steps.extract.outputs.POST_CONTENT }}

      - name: Commit and push results
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add bio_results.tsv topic_memory.json || true
          git commit -m "AutoResearch: Update results $(date)" || exit 0
          git push
        if: success()

      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            const { owner, repo } = context.repo;
            await github.rest.issues.create({
              owner,
              repo,
              title: 'AutoResearch Pipeline Failed',
              body: `The AutoResearch Bio-Medical Pipeline failed at ${{ new Date().toISOString() }}`
            });
```

## Daily Execution Workflow

If you prefer daily execution, modify the schedule:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Every day at 6 AM UTC
```

## Weekly Reports

To generate weekly reports, add this job to your workflow:

```yaml
  generate-report:
    needs: run-autoresearch
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: uv sync

      - name: Generate weekly report
        run: python autoresearch_bio.py --print-learning
        env:
          TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
          GEMINI_API_KEY_1: ${{ secrets.GEMINI_API_KEY_1 }}

      - name: Create report issue
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('weekly_report.txt', 'utf8');
            const { owner, repo } = context.repo;

            await github.rest.issues.create({
              owner,
              repo,
              title: `Weekly AutoResearch Report - ${new Date().toLocaleDateString()}`,
              body: `\`\`\`\n${report}\n\`\`\``
            });
```

## Security Considerations

1. **API Keys**: Store all API keys as GitHub Secrets, never in the workflow file
2. **Permissions**: Grant minimal required permissions to the workflow
3. **Rate Limits**: Be mindful of API rate limits when scheduling frequent executions
4. **Secret Rotation**: Regularly rotate your API keys

## Monitoring and Notifications

### Email Notifications
Add email notifications using third-party actions:

```yaml
      - name: Send email notification
        if: success()
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 465
          username: ${{ secrets.EMAIL_USERNAME }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: AutoResearch Pipeline Completed Successfully
          body: The AutoResearch Bio-Medical Pipeline completed successfully at ${{ github.event.created_at }}
          to: your-email@example.com
          from: GitHub Actions
```

### Slack Notifications
```yaml
      - name: Send Slack notification
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'AutoResearch Pipeline completed successfully!'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure your workflow has appropriate permissions
2. **API Limits**: Space out executions to respect rate limits
3. **Missing Dependencies**: Make sure all dependencies are properly installed
4. **Git Conflicts**: Handle git operations carefully to avoid conflicts

### Debugging

Enable debug logging by adding this step:

```yaml
      - name: Enable debug logging
        run: echo "ACTIONS_STEP_DEBUG=true" >> $GITHUB_ENV
```

## Best Practices

1. **Schedule Wisely**: Avoid running too frequently to respect API limits
2. **Monitor Costs**: Keep track of API usage and associated costs
3. **Backup Results**: Regularly backup important results
4. **Test Changes**: Test workflow changes before deploying to main branch
5. **Monitor Performance**: Track the quality and quantity of generated content

## Conclusion

With GitHub Actions automation, your AutoResearch Bio-Medical Pipeline can run continuously without manual intervention, automatically managing results and optionally publishing content. This setup provides reliability, persistence, and the ability to run even when your local machine is offline.