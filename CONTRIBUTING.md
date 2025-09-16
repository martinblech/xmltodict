# Contributing

We welcome contributions to this project! Please follow these guidelines to ensure a smooth and effective contribution process.

## How to Contribute

- Fork the repository.
- Create a new branch for your feature or bug fix.
- Make your changes.
- Ensure that the tests pass.
- Submit a pull request with a clear description of your changes.

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for our commit messages.
This allows for automated changelog generation and release management.

The commit message format is:
`type(scope?): subject`

The `type` must be one of the following:
- `build`: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- `chore`: Other changes that don't modify src or test files
- `ci`: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
- `docs`: Documentation only changes
- `feat`: A new feature
- `fix`: A bug fix
- `perf`: A code change that improves performance
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `revert`: Reverts a previous commit
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `test`: Adding missing tests or correcting existing tests

The `scope` is optional and can be used to specify the part of the codebase that is affected by the change.
The `subject` contains a succinct description of the change:
- Use the imperative, present tense: "add" not "added" nor "adds".
- Don't capitalize the first letter.
- No dot (.) at the end.
- The subject line must not exceed 50 characters.

The `body` of the commit message is optional and should be used to provide additional context.
- The body should be wrapped at 72 characters.
