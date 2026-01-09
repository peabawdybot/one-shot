import { test as base, expect, type Page } from '@playwright/test';

interface TestUser {
	email: string;
	password: string;
}

interface Fixtures {
	authenticatedPage: Page;
	testUser: TestUser;
	adminUser: TestUser;
}

export const test = base.extend<Fixtures>({
	testUser: async ({}, use) => {
		const user = {
			email: `test-${Date.now()}@example.com`,
			password: 'testpassword123',
		};
		await use(user);
	},

	adminUser: async ({}, use) => {
		const admin = {
			email: 'admin@example.com',
			password: 'adminpassword123',
		};
		await use(admin);
	},

	authenticatedPage: async ({ page, testUser }, use) => {
		// Register a new user
		await page.goto('/register');
		await page.fill('input[name="email"]', testUser.email);
		await page.fill('input[name="password"]', testUser.password);
		await page.click('button[type="submit"]');

		// Wait for redirect to dashboard
		await page.waitForURL('/dashboard');

		await use(page);
	},
});

export { expect };
