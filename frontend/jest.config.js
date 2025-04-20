module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  roots: ['<rootDir>/src', '<rootDir>'],
  testMatch: ['**/tests/**/*.{test,spec}.{ts,tsx,js}'],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
  },
};

