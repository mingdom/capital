# Dev Lead Process Notes - Portfolio Info Feature

**Date**: 2026-01-08
**Project**: Portfolio Information Display Feature
**Dev Lead**: Claude (first project as lead)
**Plan**: `docs/plans/2026-01-08-portfolio-info-feature.md`

---

## Project Overview

Implemented a multi-page portfolio information system with markdown-based content management. Feature adds investment philosophy, strategy/mandate, and fund background sections in an editorial-style UX.

**Key Innovation**: Built scalable multi-page architecture that supports future expansion (reports, team pages, settings, etc.)

---

## Task Breakdown Approach

### Initial Attempt (Too Granular)
- Started with 23 implementation steps from technical plan
- **Feedback from PM**: Too granular for task tracking
- **Learning**: Engineers don't need step-by-step instructions - they need verifiable feature chunks

### Final Approach (Phase-Based)
Consolidated 23 steps into **5 phases**, each representing a QA-able deliverable:

1. **Phase 1**: Multi-Page Infrastructure (foundation)
2. **Phase 2**: Content System & Markdown Processing (data layer)
3. **Phase 3**: Portfolio Info UI Components (component library)
4. **Phase 4**: Portfolio Info Page Integration (assembly)
5. **Phase 5**: Polish, Testing & Build Verification (production-ready)

**Why This Works**:
- Each phase = natural stopping point for QA review
- Engineers can own full vertical slices
- Clear dependencies and sequencing
- Verifiable acceptance criteria at phase level

---

## Bead Structure (Per Phase)

Each bead includes:

### 1. Scope Section
- Bullet list of files to create/modify
- Clear boundaries of what's in/out of scope

### 2. Acceptance Criteria
- Checkboxes for verification
- Technical requirements (TypeScript passes, no console errors)
- UX requirements (responsive, animations smooth)
- Integration requirements (works with existing system)

### 3. Reference Section
- Link to plan document with specific phase/steps
- Points to relevant sections (Design Specs, Component Design, Testing)

### 4. Testing Instructions
- How to manually verify the phase works
- Specific URLs to test
- Responsive breakpoints to check
- Edge cases to consider

---

## What Worked Well

### ✅ Phase-Level Granularity
- 5 phases feel manageable and meaningful
- Each phase has clear "definition of done"
- Natural checkpoints for code review

### ✅ Comprehensive Acceptance Criteria
- Engineers know exactly what "done" means
- QA can verify without guessing
- Reduces back-and-forth clarification

### ✅ Sequential Dependencies in bd
- Used `bd dep add` to enforce Phase 1 → 2 → 3 → 4 → 5
- Prevents engineers from jumping ahead
- Ensures foundation is solid before building on top

### ✅ Linking Plan Document
- Every bead references `docs/plans/2026-01-08-portfolio-info-feature.md`
- Engineers have full context if needed
- Single source of truth for technical details

### ✅ Labeling System
- Added `portfolio-info` and `feature` labels to all beads
- Easy filtering: `bd list --filter "label:portfolio-info"`
- Groups related work together

---

## What Could Be Improved

### ⚠️ Testing Scope Per Phase
Some phases have light testing (Phase 1-3) vs heavy testing (Phase 5). Should consider:
- **Option A**: Distribute testing more evenly across phases
- **Option B**: Keep it as-is (build fast, test thoroughly at end)
- **Decision needed**: Depends on team's preference for TDD vs integration testing

### ⚠️ Bundle Size Verification
Phase 5 includes "bundle size <50KB gzipped" but:
- How do we measure this accurately?
- Should this be automated in CI?
- **Action**: May need to document bundle analysis process

### ⚠️ Plan Document Length (30KB)
The plan is comprehensive but long. Engineers might not read it all. Consider:
- **TL;DR section** at top with 5-bullet summary
- **Quick Reference** section with just files/colors/specs
- Keep detailed explanations for edge cases

### ⚠️ Cross-Browser Testing Logistics
Phase 5 requires Safari testing but engineers may not have Macs. Need:
- BrowserStack account or similar
- Clear instructions on how to access test environments
- **Action**: Document in team wiki/onboarding

---

## Process Workflow Used

1. **Planning Phase** (with PM approval)
   - Used frontend-design skill to explore UX direction
   - Researched institutional fund documentation patterns
   - Created comprehensive plan with mockups and examples
   - Got PM approval before task breakdown

2. **Task Breakdown**
   - Received feedback: "Think in verifiable feature chunks, not steps"
   - Consolidated 23 steps → 5 phases
   - Each phase = natural QA checkpoint

3. **Bead Creation**
   - Used `bd create` with structured body (Scope, Acceptance, Reference, Testing)
   - Added sequential dependencies: `bd dep add [phase-N] [phase-N-1]`
   - Applied labels for grouping: `bd label add [ids...] portfolio-info`

4. **Documentation**
   - Created this process doc in `docs/process/`
   - Goal: Learn and improve for next project

---

## Recommendations for Next Feature

### For Planning
- ✅ Keep comprehensive technical plans (useful reference)
- ➕ Add TL;DR section at top for quick scanning
- ➕ Include "Definition of Done" checklist in plan

### For Task Breakdown
- ✅ Use phase-based approach (3-5 phases, not 20+ steps)
- ✅ Each phase = QA-able vertical slice
- ➕ Consider adding time estimates (even rough ones)
- ➕ Identify critical path vs nice-to-have

### For Beads
- ✅ Comprehensive acceptance criteria (keep doing this)
- ✅ Testing instructions per phase (keep doing this)
- ➕ Add "estimated effort" field (hours or t-shirt size)
- ➕ Consider adding "related files" section for quick navigation

### For Communication
- ➕ Share plan summary with team before starting
- ➕ Create Slack/discussion channel for feature-specific questions
- ➕ Set up weekly sync to review progress and blockers

---

## Open Questions for PM

1. **Testing Strategy**: Should we enforce tests per phase, or bundle testing in Phase 5?
2. **Code Review**: Who reviews each phase? Should phases be reviewed sequentially or can they be parallel?
3. **Documentation**: Is plan document the right level of detail, or do engineers want something lighter?
4. **Tooling**: Should we automate bundle size checking, or is manual verification OK?
5. **Definition of Done**: Are the acceptance criteria clear enough, or should I add more?

---

## Key Metrics

- **Plan Size**: 30KB markdown
- **Phases Created**: 5 beads
- **Files to Create**: ~10 new files
- **Files to Modify**: 4 existing files
- **Dependencies Added**: 4 sequential blocks
- **Labels Applied**: 2 (portfolio-info, feature)

---

## Next Steps (For Me as Dev Lead)

1. ✅ Created beads and dependencies
2. ✅ Documented process learnings
3. ⏳ **Wait for Phase 1 completion by jr engineer**
4. ⏳ Review Phase 1 code quality and acceptance criteria
5. ⏳ Provide feedback and unblock Phase 2
6. ⏳ Repeat for Phases 2-5
7. ⏳ Final E2E QA before marking feature complete

---

## Reflection

**What I learned**:
- Task breakdown is an art - need to match engineer's mental model, not just break down technical steps
- Acceptance criteria are critical - they define "done" and prevent scope creep
- Sequential dependencies help ensure quality foundation before building up
- Documentation is for future me (and the team) - write it while context is fresh

**What surprised me**:
- PM pushed back on granular tasks (good learning - trust engineers more)
- bd tool is very flexible (labels, deps, custom fields)
- Process documentation itself is valuable (helps me improve)

**What I'd do differently next time**:
- Start with "what are the QA checkpoints?" and work backward
- Add rough time estimates to help PM with scheduling
- Create a lighter "Quick Start" version of plan for engineers who want less detail

---

**Status**: Ready to hand off to jr engineers for implementation
**Next Review**: After Phase 1 completion
