# Contributing to LibreDomains

Thank you for your interest in contributing to LibreDomains! This document provides guidelines for different types of contributions.

## 🚀 For Users (Subdomain Requests)

### Quick Start

1. **Fork this repository**
2. **Create your request file** in `requests/` directory
3. **Submit a Pull Request**
4. **Wait for automated validation and approval**

### Request File Format

Create a JSON file named `your-subdomain.json` in the `requests/` directory:

```json
{
  "domain": "ciao.su",
  "subdomain": "your-subdomain",
  "owner": {
    "username": "your-github-username",
    "email": "your-email@example.com"
  },
  "record": {
    "type": "A",
    "value": "192.168.1.1",
    "ttl": 3600,
    "proxied": false
  },
  "description": "Brief description of your subdomain usage"
}
```

### Examples

Check the `requests/` directory for example files:
- `example-personal-website.json` - Personal website with CNAME
- `example-api-service.json` - API service with A record
- `example-mail-server.json` - Mail server with MX record
- `example-ipv6-website.json` - IPv6 website with AAAA record

## 👨‍💻 For Developers

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/LibreDomains-beta.git
   cd LibreDomains-beta
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   export CLOUDFLARE_API_TOKEN="your-token-here"
   ```

### Testing

```bash
# Test request validation
npm run validate requests/example-personal-website.json

# Test GitHub user checking
npm run check-user your-username

# Test DNS deployment (requires API token)
npm run deploy deploy requests/example-personal-website.json
```

### Code Style

- Use ES6+ features
- Follow existing code patterns
- Add comments for complex logic
- Use meaningful variable names

### Pull Request Process

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Update documentation if needed
5. Submit PR with clear description

## 🔧 Types of Contributions

### 1. Bug Reports

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Node.js version, etc.)

### 2. Feature Requests

For new features:
- Explain the use case
- Describe the proposed solution
- Consider backwards compatibility
- Discuss implementation approach

### 3. Documentation

Documentation improvements are always welcome:
- Fix typos and grammar
- Add missing information
- Improve examples
- Update outdated content

### 4. Code Contributions

Code contributions can include:
- Bug fixes
- New features
- Performance improvements
- Code cleanup and refactoring

## 📏 Contribution Guidelines

### Do's ✅

- Follow the existing code style
- Write clear commit messages
- Test your changes thoroughly
- Update documentation when needed
- Be respectful in discussions
- Use meaningful PR titles

### Don'ts ❌

- Don't submit large PRs without discussion
- Don't break existing functionality
- Don't ignore CI/CD failures
- Don't submit incomplete features
- Don't use offensive language

## 🔍 Review Process

1. **Automated Checks**
   - Schema validation
   - Format checking
   - User verification

2. **Maintainer Review**
   - Code quality
   - Security considerations
   - Feature completeness

3. **Approval & Merge**
   - Final approval by maintainer
   - Automatic deployment

## 🚨 Reporting Issues

### Security Issues

For security vulnerabilities:
- **DO NOT** create public issues
- Email security@libredomains.org
- Include detailed description
- Wait for response before disclosure

### Regular Issues

For bugs and feature requests:
- Use GitHub Issues
- Use appropriate labels
- Provide clear descriptions
- Include reproduction steps

## 📞 Getting Help

- **Documentation**: Check README and docs/
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our community channels

## 🏆 Recognition

Contributors will be:
- Listed in README
- Mentioned in release notes
- Invited to maintainer team (active contributors)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making LibreDomains better! 🎉
