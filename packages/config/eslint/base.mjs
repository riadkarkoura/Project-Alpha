import js from "@eslint/js";

/** Shared flat ESLint config extended by non-Next.js workspace packages. */
export default [
  js.configs.recommended,
  {
    ignores: ["dist/**", "node_modules/**"],
  },
];
