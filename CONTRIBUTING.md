First off, thanks for taking the time to contribute!


#### Table Of Contents

- [Code of Conduct](#code-of-conduct)
- [I Don't Want to Read This Whole Thing, I Just Have a Question!!!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)
- [What Should I Know Before I Get Started?](#what-should-i-know-before-i-get-started)
  - [Packages](#packages)
  - [Design Decisions](#design-decisions)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Styleguides](#styleguides)
  - [Git Commit Messages](#git-commit-messages)
  - [Python Styleguide](#python-styleguide)
  - [Documentation Styleguide](#documentation-styleguide)
- [Additional Notes](#additional-notes)
  - [Issue and Pull Request Labels](#issue-and-pull-request-labels)
- [Attribution](#attribution)

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to **@rreinecke**.

## I don't want to read this whole thing, I just have a question!!!
If you have a software issue please take a look at the open issues. If your isn't mentioned yet feel free to contact **@rreinecke** directly.

## What should I know before I get started?

### Packages

Install the required packages using: 

```bash
pip install -r requirements.txt
```
### Design Decisions

### Design Decisions

Understanding the project's design principles will help you align your contributions:

- **Streamlit for Interactive Front-End**: The project uses **Streamlit** to create a user-friendly and interactive web interface. This allows the presentation of groundwater models, data visualization, and user inputs through an accessible, Python-based framework. Contributors should ensure that new features maintain compatibility with Streamlit's functionality and follow best practices for building intuitive user interfaces.

- **Modular Architecture**: The application is organized into modules, each handling specific aspects of the project, such as data retrieval, visualization, and user interactions. This modular approach allows for easier maintenance and scalability of the codebase.

- **Community-Driven Data Collection**: GroMoPo relies on contributions from the global groundwater modeling community. The design focuses on ease of data submission and review, making it straightforward for users to contribute new groundwater models.

- **Test-Driven Development (TDD)**: We prioritize writing tests alongside code to ensure that both the front-end and back-end components function as expected. Automated tests help maintain the reliability of the project as new features are added.

- **Data Integration with HydroShare**: The project integrates closely with **HydroShare**, where the groundwater model data is hosted. Contributions that involve data handling should consider the compatibility with HydroShare's APIs and data formats.

- **Code Readability and Maintainability**: Clean and readable code is highly valued. We prioritize clarity and consistency over clever shortcuts, making it easier for new contributors to understand and work on the codebase.

## How Can I Contribute?
If you want to become a full contributor please PM rreinecke
### Reporting Bugs
Please use the issue tracking system and this template:
```
### Overview Description

# Steps to Reproduce

1.
2.
3.

# Actual Results

# Expected Results

# Reproducibility

# Additional Information:
```

### Suggesting Enhancements

Have an idea to improve the project? We’d love to hear it! To suggest an enhancement:

1. **Search Existing Issues**: Before suggesting a new feature, please check the [existing issues](https://github.com/Gromopo/GroMoPo/issues) to see if a similar suggestion has been made.
2. **Create a New Issue**: If your suggestion is unique, open a new issue with a clear and detailed description of the enhancement.
3. **Describe the Use Case**: Explain why this feature would be useful for users or developers.
4. **Be Open to Discussion**: Engage in any discussions related to your suggestion. We value feedback from the community!

### Your First Code Contribution

Ready to make your first contribution? Follow these steps:

1. **Fork the Repository**: Click the "Fork" button on the project page.
2. **Clone Your Fork**:
```bash
git clone https://github.com/your-username/GroMoPo/
```
3. **Create a Branch**: Use a descriptive name for your branch.
```bash
git checkout -b branch_name
```
4. **Make Changes**: Implement your feature or fix a bug.
5. **Write Tests**: Make sure new code is covered by tests.
6. **Commit Your Changes**: Use a clear and concise commit message.
```bash
git commit -m “Add feature that does X”
```
7. **Push Your Changes**:
```bash
git push origin branch_name
```
8. **Open a Pull Request**: Go to the original repository and open a pull request. Fill in the template and provide a detailed description of your changes.

### Pull Requests

Pull requests (PRs) are the best way to propose changes:

- **Link to Issues**: Reference any relevant issue numbers (e.g., `Closes #123`).
- **Include Tests**: If you add new features or fix bugs, include tests to verify your changes.
- **Follow the Styleguides**: Make sure your code adheres to the project's style guidelines.
- **Be Responsive**: Engage with any feedback or review comments on your PR.

```bash
Add validation for user input in form

Ensures that user input is properly validated before submission.
Fixes #123.
```

## Styleguides
### Git Commit Messages
### Python Styleguide
### Documentation Styleguide

## Additional Notes
### Issue and Pull Request Labels

## Attribution
Adapted from the [Atom editor](https://github.com/atom) project

