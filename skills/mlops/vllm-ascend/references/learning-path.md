# vLLM-Ascend Learning Path

## Quick Start (Day 1)

1. **Read core documentation**
   - README.md - Project overview, prerequisites, quick start
   - CONTRIBUTING.md - Contribution guidelines
   - docs/source/quick_start.md - Setup instructions

2. **Understand architecture**
   - Review inheritance hierarchy (CRITICAL)
   - Read `vllm_ascend/platform.py` - Platform abstraction
   - Read `vllm_ascend/worker/worker.py` - Worker process
   - Read `vllm_ascend/worker/model_runner_v1.py` - Model runner

3. **Check inheritance before ANY implementation**
   - See [inheritance-check-workflow.md](inheritance-check-workflow.md)
   - NPUPlatform inherits Platform → auto-inherits all methods
   - Check base class before adding new methods

## First Week

### Read Merged PRs (3-5)
Recommended:
- PR #9149 - BugFix: BalanceScheduler deadlock (validation check placement)
- PR #9199 - BugFix: Version suffix comparison (robust version handling)
- PR #9216 - Feature: Worker shutdown (checking dependencies, NPU-specific logic)

Learn from each:
- Code style and patterns
- Test structure
- How Gemini feedback was addressed
- CI failure resolution

### Read Issues (3-5)
Recommended:
- Issue #8975 - Clear bug, single validation check needed
- Issue #9167 - Utility function fix, version handling
- Issue #3489 - **Learn from mistake**: Check inheritance first!
- Issue #4112 - Interface addition, check dependencies

### Run Tests
```bash
# Unit tests (no NPU needed)
pytest tests/ut/ -v

# Specific test
pytest tests/ut/test_platform.py::TestNPUPlatform -v

# Understand test patterns
cat tests/ut/test_platform.py | head -100
```

## Second Week

### Deep Dive One Module
Choose based on interest:
- `attention/` - Attention implementations (attention_v1.py, mla_v1.py)
- `quantization/` - Quantization methods (w8a8_mxfp8.py, w4a16.py)
- `ops/` - Custom operators (fused_moe/, linear.py)
- `compilation/` - ACL Graph optimization

### Fix a Simple Issue
1. Find Good First Issue or Help Wanted label
2. Follow complete workflow:
   - Check inheritance (if adding interface)
   - Check dependencies
   - Implement + add tests
   - ruff format
   - Handle Gemini feedback
   - Monitor CI

## Ongoing Learning

### Key Resources

**Official Documentation**
- vLLM-Ascend: https://docs.vllm.ai/projects/ascend/
- vLLM: https://docs.vllm.ai/
- CANN: https://www.hiascend.com/document/

**Code Repositories**
- vLLM-Ascend: https://github.com/vllm-project/vllm-ascend
- vLLM: https://github.com/vllm-project/vllm

**Community**
- User Forum: https://discuss.vllm.ai/c/hardware-support/vllm-ascend-support
- GitHub Issues: Search by label (good first issue, help wanted, bug)

### Important Concepts

**1. Inheritance (MOST IMPORTANT)**
- NPUPlatform(Platform) - auto-inherits all Platform methods
- NPUWorker inherits Worker
- NPUModelRunner inherits GPUModelRunner
- **Always check base class before implementing**

**2. Platform-Specific Code**
- 310P has separate implementations in `_310p/`
- A2/A3/A5 may need different operators
- Check hardware-specific files when CI fails on specific platform

**3. Testing**
- Unit tests in `tests/ut/` - no NPU needed
- E2E tests in `tests/e2e/` - requires NPU
- Always add tests for new features

**4. CI/CD**
- Lint: ruff format, ruff check, mypy
- Unit tests: pytest tests/ut/
- E2E tests: platform-specific (310p, A2, etc.)
- **Network failures are NOT code problems** - retry CI

**5. Code Style**
- Match existing style in each file
- Type annotations: mixed, follow surrounding code
- Docstrings: optional but recommended
- Format: always run `ruff format` before commit

### Common Mistakes to Avoid

1. **Not checking inheritance** → Implement redundant method → PR rejected
2. **Not checking dependencies** → Call non-existent method → AttributeError
3. **Not adding tests** → PR incomplete → User asks "为什么没有增加用例"
4. **Not from main** → Include previous commits → PR shows 36 files instead of 2
5. **Not handling Gemini feedback** → Miss improvements → Lower code quality

### Verification Checklist

Before creating PR:
- [ ] Created clean branch from main
- [ ] Checked inheritance (if adding interface method)
- [ ] Checked dependencies exist
- [ ] Implemented feature/fix
- [ ] Added unit tests
- [ ] Ran `ruff format`
- [ ] Verified `git diff --stat` is minimal
- [ ] Committed with `-s` (sign-off)
- [ ] Pushed to new branch
- [ ] Created PR
- [ ] Waited for Gemini feedback
- [ ] Addressed all feedback
- [ ] CI passes (or retried if network failure)

## Learning from Mistakes

### Issue #3489 / PR #9205 - Inheritance Mistake

**What happened**: Implemented `get_vit_attn_backend` without checking Platform base class.

**Why it was wrong**: Platform base class already has this method. NPUPlatform inherits it automatically.

**Lesson**: ALWAYS check base class before implementing. Use:
```bash
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def <method_name>"
```

**Result**: PR rejected, issue closed as "not needed".

### PR #9149 - CI Network Failure

**What happened**: CI failed with `IncompleteRead` error during pip install.

**Why it looked like code problem**: CI showed red X.

**Reality**: Network timeout downloading mypy - infrastructure issue.

**Lesson**: Check error message. "Connection broken", "IncompleteRead", "timeout" = network problem. Retry CI.

## Next Steps

1. Read [inheritance-check-workflow.md](inheritance-check-workflow.md) thoroughly
2. Run `pytest tests/ut/test_platform.py -v` to understand test patterns
3. Pick a Good First Issue and follow complete workflow
4. Learn from PR reviews (both automated and maintainer feedback)
5. Continue building expertise through practice

## Reference Files in This Skill

- [inheritance-check-workflow.md](inheritance-check-workflow.md) - CRITICAL: Check before adding methods
- [pr-patterns.md](pr-patterns.md) - PR patterns from 3168+ commits
- [debugging-patterns.md](debugging-patterns.md) - Common BugFix patterns
- [architecture.md](architecture.md) - Detailed architecture diagrams
- [testing-environment-setup.md](testing-environment-setup.md) - CI images, Docker setup
