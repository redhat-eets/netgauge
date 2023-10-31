# Contributing to netgauge

All contributions are valued and welcomed, whether they come in the form of code, documentation, ideas or discussion.
While we have not applied a formal Code of Conduct to this, or related, repositories, we require that all contributors
conduct themselves in a professional and respectful manner.

## Issues

The easiest way to contribute to netgauge is through Issues. This could be by making a suggestion, reporting a
bug, or helping another user.

### Suggestions

To make a suggestion open an Issue in the GitHub repository describing what feature/change you think is needed, why, and
if possible give an example.

### Bug Reports

> ❗ _Red Hat does not provide commercial support for the content of this repo. Any assistance is purely on a best-effort basis, as resources permit._

If you encounter a bug then carefully examine the output. If you choose to open an issue then please include as much
information about the problem as possible, as this gives the best chance someone can help. We suggest:

- A description of your environment
- A copy of your report and standard output

**This may include data you do not wish to share publicly.** In this case a more private forum is suggested.

## Workflow

The required workflow for making a contribution is Fork-and-Pull. This is well documented elsewhere but to summarize:

1. Create a fork of this repository.
1. Make and test the change on your fork.
1. Submit a Pull Request asking for the change to be merged into the main repository.

How to create and update a fork is outside the scope of this document but there are plenty of
[in-depth](https://gist.github.com/Chaser324/ce0505fbed06b947d962)
[instructions](https://reflectoring.io/github-fork-and-pull/) explaining how to go about it.

All contributions must have as much test coverage as possible and include relevant additions and changes to both
documentation and tooling. Once a change is implemented, tested, documented, and passing all checks then submit a Pull
Request for it to be reviewed.

## Peer review

At least two maintainers must "Accept" a Pull Request prior to merging a Pull Request. No Self Review is allowed. The
maintainers of netgauge are:

- Jianzhu Zhang (jianzzha)
- Daniel Kostecki (dkosteck)
- Andrew Kiselev (akiselev1)

All contributors are strongly encouraged to review Pull Requests. Everyone is responsible for the quality of what is
produced, and review is also an excellent opportunity to learn.

## Commits and Pull Requests

A good commit does a *single* thing, does it completely, concisely, and describes *why*.

The commit message should explain both what is being changed and, in the case of anything non-obvious, why that change
was made. Commit messages are something that has been extensively written about so need not be discussed in more detail
here, but contributors should follow [these seven rules](https://chris.beams.io/posts/git-commit/#seven-rules) and keep
individual commits focussed.

A good Pull Request is the same; it also does a *single* thing, does it completely, and describes *why*. The difference
is that a Pull Request may contain one or more commits that together prepare for and deliver a feature.

Once a branch has been code reviewed, we encourage the branch’s author to use an interactive rebase to squash the branch
down into a few commits with meaningful commit messages. It’s fairly common for a feature branch to be squashed down to
somewhere between one and three commits before it’s merged.

## Style Guidelines

- Favor readability over brevity in both naming and structure
- Document the _why_ with comments, and the _what_ with clear code
- When in doubt, follow the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code

## Validating Changes

All netgauge project tools should be validated to work and, in cases where changes affect common code, that changes do not break existing tools or common code. To this end there are GitHub Actions running to validate formatting by way of linters, as well as an option to run actual performance tests on a lab machine. The linters run automatically on Pull Requests.

Contributors are encouraged to run linters locally first in order to minimize CI failures in their pull request. Python code is validated by [flake8](https://flake8.pycqa.org/en/latest/). The following flake8 call is used in the linter workflow:

`flake8 rfc2544 --count --select=E,C,F,W --ignore W503 --max-complexity=15 --max-line-length=88 --show-source --statistics`

[black](https://black.readthedocs.io/en/stable/) is another helpful Python code formatter tool, which you may want to use in case of numerous flake8 formatting complaints.

Golang code is validated using [golangci-lint](https://golangci-lint.run/) Github action. That can also can run locally prior to CI run, for example:

`cd testpmd
golangci-lint run -D unused,errcheck -v`

The optional "real" rfc2544 trafficgen testing can be run by applying "trafficgen-test" label to a Pull Request. This will start an action which queues a performance trafficgen test. 

"trafficgen-test" label triggers a performance test execution using 710-series NIC ports over the switch loopback. By default this test will pass if RX drop rate is less than 50%. Alternatively, "traffic-test-<RX drop %>" label can be used for custom RX drop rate limit performance test. For example, "trafficgen-test-10" will pass with RX drop rate below 10% of max L1 rate recorded for 25G link in this setup. Label-triggered performance test uses TREX version 2.88.

Trafficgen-test workflow can also be triggered on demand on any selected branch using workflow_dispatch event trigger. That allows selecting 2.88 or 3.02 TREX version and entering acceptable RX line rate drop in % from max L1 rate for that interface. 

Likewise, "e2e-testpmd" label will trigger an end-to-end test execution, covering both trafficgen and testpmd tools. These tools will run on two different servers, connected by back-to-back 25G links. This test uses DPDK version 21.11.2 (can be changed in case of on demand execution), TREX version 2.88 and minimum acceptable RX line rate of 9 Gbps on a 25G link.

Because these tests take both time and resources, they should only be started after a PR is ready to merge as a final check of functionality. This label should only be utilized by repository maintainers. After the test run, check the results of the Actions workflows and rerun tests, if needed.

