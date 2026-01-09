# iOS Safari Responsive Design Fix Plan

**Date**: January 8, 2026
**Status**: ✅ Fix Implemented - Ready for Testing

## Changes Made

The Mingdom Capital dashboard displays correctly on desktop browsers (including mobile simulation mode), but on actual iOS Safari devices, it renders the desktop layout instead of the mobile layout. The user sees 4 cards per row instead of 2, and everything appears tiny.

## Technical Analysis

### Verified Working ✅
1. **Viewport meta tag IS present** in the generated HTML:
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes, viewport-fit=cover">
   ```
2. **Media queries ARE generated** in the CSS:
   - `min-width: 640px` (sm breakpoint)
   - `min-width: 768px` (md breakpoint)
   - `min-width: 1024px` (lg breakpoint)
   - etc.
3. **Desktop Browser Mobile Simulation** works correctly (responsive layout triggers)

### What We Tried (Did NOT Fix)
| Attempt | Description | Result |
|---------|-------------|--------|
| Tailwind v4 @source | Added `@source` directive to scan component files | Media queries generated but iOS still broken |
| Tailwind v4 @theme | Added explicit breakpoint definitions | No effect on iOS |
| Viewport export | Used Next.js 14+ `export const viewport` | Viewport meta present but iOS ignores it |
| Explicit `<head>` meta | Added duplicate viewport meta in layout | No effect |
| IOSViewportFix component | Client-side script to force viewport | No effect |
| Tailwind v3 downgrade | Reverted to Tailwind v3 | User reverted - prefers v4 |
| iOS CSS fixes | Added `-webkit-text-size-adjust: 100%` etc. | No effect |

## Root Cause Hypothesis

Based on web research, iOS Safari has a specific behavior:
1. By default, it renders pages at **980px wide** (virtual viewport)
2. It then scales down to fit the screen
3. The viewport meta tag should override this, but something is preventing it

**Possible causes**:
1. **"Request Desktop Site" is enabled** in iOS Safari settings (per-site or globally)
2. **The viewport meta tag order** - iOS may be reading multiple viewport tags and using the wrong one
3. **Next.js static export** may have a specific iOS Safari bug
4. **The explicit `<head>` tag in layout.tsx** may conflict with Next.js's meta generation

## Proposed Solution

### Option A: Remove Duplicate Viewport Meta (HIGH CONFIDENCE)
The layout.tsx currently has BOTH:
1. `export const viewport = {...}` (Next.js 14+ way)
2. Explicit `<meta name="viewport" ...>` in `<head>`

This could confuse iOS Safari. **Remove the explicit `<head>` block** and rely solely on the Next.js viewport export.

### Option B: Check for iOS Safari "Desktop Site" Mode
This is a user-side issue. The user may need to:
1. Open Safari on iOS
2. Tap the "aA" button in the URL bar
3. Ensure "Request Desktop Website" is OFF
4. Or go to Settings → Safari → Request Desktop Website → Turn off for "All Websites"

### Option C: Use `shrink-to-fit=no`
Add `shrink-to-fit=no` to the viewport meta tag (Safari-specific fix).

## Implementation Plan

1. **Clean up layout.tsx**: Remove the duplicate explicit viewport meta
2. **Update viewport export**: Add `shrink-to-fit=no` variant
3. **Test locally** with `npm run build`
4. **Provide user with Safari settings to check**

## Files to Modify
- `web/app/layout.tsx` - Remove explicit `<head>` with viewport meta, update viewport export
- `web/components/ios-viewport-fix.tsx` - May remove if not needed
