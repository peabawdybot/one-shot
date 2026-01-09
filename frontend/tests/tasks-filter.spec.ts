import { test, expect } from '@playwright/test';

test.describe('Task Status Filtering', () => {
	test.beforeEach(async ({ page }) => {
		// Register a new user
		const email = `test-${Date.now()}@example.com`;
		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');
	});

	test('mark task complete - shows visual indicator', async ({ page }) => {
		// Create a task
		await page.click('text=+ New Task');
		await page.fill('input#title', 'Task to complete');
		await page.click('button:text("Add Task")');
		await expect(page.locator('text=Task to complete')).toBeVisible();

		// Mark complete
		await page.click('button[aria-label="Mark complete"]');

		// Should show as completed (has checkmark icon)
		await expect(page.locator('button[aria-label="Mark incomplete"]')).toBeVisible();
	});

	test('filter by completed - shows only completed tasks', async ({ page }) => {
		// Create two tasks
		await page.click('text=+ New Task');
		await page.fill('input#title', 'Active task');
		await page.click('button:text("Add Task")');

		await page.click('text=+ New Task');
		await page.fill('input#title', 'Completed task');
		await page.click('button:text("Add Task")');

		// Mark one as complete
		const completedTaskRow = page.locator('text=Completed task').locator('..');
		await completedTaskRow.locator('button[aria-label="Mark complete"]').click();

		// Filter by completed
		await page.click('button:text("Completed")');

		// Should only see completed task
		await expect(page.locator('text=Completed task')).toBeVisible();
		await expect(page.locator('text=Active task')).not.toBeVisible();
	});

	test('filter by active - shows only incomplete tasks', async ({ page }) => {
		// Create two tasks
		await page.click('text=+ New Task');
		await page.fill('input#title', 'Active task');
		await page.click('button:text("Add Task")');

		await page.click('text=+ New Task');
		await page.fill('input#title', 'Completed task');
		await page.click('button:text("Add Task")');

		// Mark one as complete
		const completedTaskRow = page.locator('text=Completed task').locator('..');
		await completedTaskRow.locator('button[aria-label="Mark complete"]').click();

		// Filter by active
		await page.click('button:text("Active")');

		// Should only see active task
		await expect(page.locator('text=Active task')).toBeVisible();
		await expect(page.locator('text=Completed task')).not.toBeVisible();
	});

	test('mark task incomplete - removes completed indicator', async ({ page }) => {
		// Create a task
		await page.click('text=+ New Task');
		await page.fill('input#title', 'Toggle task');
		await page.click('button:text("Add Task")');

		// Mark complete
		await page.click('button[aria-label="Mark complete"]');
		await expect(page.locator('button[aria-label="Mark incomplete"]')).toBeVisible();

		// Mark incomplete again
		await page.click('button[aria-label="Mark incomplete"]');
		await expect(page.locator('button[aria-label="Mark complete"]')).toBeVisible();
	});
});
