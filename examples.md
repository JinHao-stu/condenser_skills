# Think Condenser Examples

## Example 1: Live thinking — code debug

**Before (verbose reasoning):**
```
让我先思考一下这个问题。首先，我需要理解用户的报错信息。其次，我认为这个错误可能是因为
空指针导致的。让我再仔细看看 stack trace。综上所述，应该在 UserService.getById 里加空检查。
```

**After (compressed):**
```
Goal: fix NPE in user lookup
Error: NullPointerException at UserService.getById:42
Hypothesis: id null or missing row not handled
Action: add null guard in UserService.getById before dereference
```

## Example 2: Live thinking — English refactor task

**Before:**
```
Let me analyze this. First, I need to understand the requirements. I think the user wants to
extract the validation logic. Therefore, we should move it to a separate module. In other words,
create validators.py and import from there.
```

**After:**
```
Task: extract validation logic → validators.py
Steps: (1) create validators.py (2) move validate_* functions (3) update imports in routes.py
Keep public API unchanged
```

## Example 3: Script — Chinese meta removal

**Input:**
```
让我思考一下这个问题。首先，我需要理解用户的需求。其次，这个问题简单来说就是如何优化代码。
综上所述，我们需要重构这个类。
```

**Output (balanced):**
```
理解用户需求。问题优化代码。重构类。
```

## Example 4: What NOT to compress

**Keep intact:**
```
Error: HTTP 403 on POST /api/admin/users — missing scope "users:write"
Constraint: do NOT use --no-verify on commit
Branch: if env=prod → require MFA; else skip
File: src/auth/middleware.ts:87
```

Removing `403`, `not`, `if/else`, or the path would break execution quality.

## Example 5: Duplicate sentence removal

**Before:**
```
The cache key must include userId. We need userId in the cache key.
TTL should be 300 seconds. Cache TTL: 300s.
```

**After:**
```
Cache key: include userId
TTL: 300s
```
