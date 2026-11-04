import js from '@eslint/js'
import reactPlugin from 'eslint-plugin-react'
import reactHooksPlugin from 'eslint-plugin-react-hooks'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import vitest from '@vitest/eslint-plugin'

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['src/**/*.{ts,tsx}', 'tests/**/*.{ts,tsx}'],
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooksPlugin,
    },
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    rules: {
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'error',
    },
    settings: {
      react: { version: 'detect' },
    },
  },
  {
    files: ['tests/**/*.{ts,tsx}', 'src/**/*.test.{ts,tsx}'],
    plugins: { vitest },
    rules: {
      'vitest/no-disabled-tests': 'error',
      'vitest/no-focused-tests': 'error',
    },
  },
  {
    ignores: ['out/', 'dist/', 'node_modules/'],
  },
)
