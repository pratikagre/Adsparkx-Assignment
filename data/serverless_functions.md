# Deploying Serverless Functions

Adsparkx Serverless Functions allow you to run backend code without managing servers.

## Limitations
- **Max Execution Timeout**: 15 seconds for Free Tier, 300 seconds for Enterprise.
- **Memory Limit**: 512MB by default.
- **Language Support**: Node.js 18+, Python 3.10+, Go 1.20+.

## Environment Variables
Do not hardcode API keys or secrets in your serverless code. Instead:
1. Go to Settings > Environment Variables in the console.
2. Add your secrets.
3. Retrieve them in code using `os.environ.get("MY_SECRET")`.
