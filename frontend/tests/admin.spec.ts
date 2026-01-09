import { test, expect } from '@playwright/test';

test.describe('Admin Panel', () => {
	test('non-admin user cannot access admin panel', async ({ page }) => {
		// Register as regular user
		const email = `user-${Date.now()}@example.com`;
		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');

		// Try to navigate to admin
		await page.goto('/admin');

		// Should redirect to dashboard
		await page.waitForURL('/dashboard');
	});

	test('admin link only shows for admin users', async ({ page }) => {
		// Register as regular user
		const email = `user-${Date.now()}@example.com`;
		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');

		// Admin link should not be visible
		await expect(page.locator('a[href="/admin"]')).not.toBeVisible();
	});
});
