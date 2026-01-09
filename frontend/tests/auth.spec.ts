import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
	test('register flow - creates account and redirects to dashboard', async ({ page }) => {
		const email = `test-${Date.now()}@example.com`;

		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');

		await page.waitForURL('/dashboard');
		await expect(page.locator('text=My Tasks')).toBeVisible();
	});

	test('login flow - authenticates and redirects to dashboard', async ({ page }) => {
		const email = `test-${Date.now()}@example.com`;

		// First register
		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');

		// Logout
		await page.click('text=Logout');
		await page.waitForURL('/login');

		// Login again
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');

		await page.waitForURL('/dashboard');
		await expect(page.locator('text=My Tasks')).toBeVisible();
	});

	test('logout flow - clears session and redirects to login', async ({ page }) => {
		const email = `test-${Date.now()}@example.com`;

		// Register and login
		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');

		// Logout
		await page.click('text=Logout');

		await page.waitForURL('/login');
		await expect(page.locator('text=Login')).toBeVisible();
	});

	test('protected route - redirects unauthenticated users to login', async ({ page }) => {
		await page.goto('/dashboard');

		// Should redirect to login
		await page.waitForURL('/login');
	});

	test('register - shows error for duplicate email', async ({ page }) => {
		const email = `test-${Date.now()}@example.com`;

		// First registration
		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');

		// Logout and try to register again with same email
		await page.click('text=Logout');
		await page.waitForURL('/login');

		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'anotherpassword123');
		await page.click('button[type="submit"]');

		await expect(page.locator('text=already registered')).toBeVisible();
	});

	test('login - shows error for invalid credentials', async ({ page }) => {
		await page.goto('/login');
		await page.fill('input[name="email"]', 'nonexistent@example.com');
		await page.fill('input[name="password"]', 'wrongpassword');
		await page.click('button[type="submit"]');

		await expect(page.locator('text=Invalid')).toBeVisible();
	});
});
