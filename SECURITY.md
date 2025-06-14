# Security Policy

## Important Security Information

### API Credentials

**NEVER share your TickTick API credentials (client ID and client secret) with anyone!**

Each user must:
1. Register their own application at https://developer.ticktick.com/manage
2. Use their own client ID and client secret
3. Keep these credentials secure and private

### Best Practices

1. **Never commit credentials to Git**
   - Use environment variables or config files
   - Config files are gitignored by default
   - Check .gitignore before committing

2. **Secure Storage**
   - TickTask stores tokens encrypted on disk
   - Token files are created with restricted permissions (600)
   - Tokens are stored in `~/.ticktask/` directory

3. **Environment Variables**
   ```bash
   export TICKTICK_CLIENT_ID="your_id"
   export TICKTICK_CLIENT_SECRET="your_secret"
   ```

4. **Config File Security**
   - Store config in `~/.ticktask/config.yaml`
   - Set file permissions: `chmod 600 ~/.ticktask/config.yaml`
   - Never share your config file

### What's Safe to Share

✅ Safe to share:
- This source code
- Bug reports (without credentials)
- Feature requests
- Usage examples (with redacted credentials)

❌ Never share:
- Your client ID
- Your client secret
- Your access tokens
- Your config files
- Any file from ~/.ticktask/

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do NOT** create a public issue
2. Email the maintainer directly
3. Include details about the vulnerability
4. Allow time for a fix before public disclosure

## OAuth2 Security

TickTask uses OAuth2 for authentication:
- Credentials are only used to obtain access tokens
- Access tokens are temporary and can be revoked
- Refresh tokens are stored encrypted
- All tokens are user-specific

Remember: Your TickTick account security depends on keeping your credentials private!