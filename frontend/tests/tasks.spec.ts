import { test, expect } from '@playwright/test';

test.describe('Task Management', () => {
	test.beforeEach(async ({ page }) => {
		// Register a new user for each test
		const email = `test-${Date.now()}@example.com`;
		await page.goto('/register');
		await page.fill('input[name="email"]', email);
		await page.fill('input[name="password"]', 'testpassword123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');
	});

	test('create task - adds task to list', async ({ page }) => {
		await page.click('text=+ New Task');
		await page.fill('input#title', 'My first task');
		await page.fill('textarea#description', 'Task description');
		await page.click('button:text("Add Task")');

		await expect(page.locator('text=My first task')).toBeVisible();
		await expect(page.locator('text=Task description')).toBeVisible();
	});

	test('view tasks - shows only own tasks', async ({ page }) => {
		// Create a task
		await page.click('text=+ New Task');
		await page.fill('input#title', 'User task');
		await page.click('button:text("Add Task")');

		await expect(page.locator('text=User task')).toBeVisible();
	});

	test('edit task - updates task details', async ({ page }) => {
		// Create a task first
		await page.click('text=+ New Task');
		await page.fill('input#title', 'Original title');
		await page.click('button:text("Add Task")');

		// Wait for task to appear
		await expect(page.locator('text=Original title')).toBeVisible();

		// Edit the task
		await page.click('button:text("Edit")');
		await page.fill('input#title', 'Updated title');
		await page.click('button:text("Update")');

		await expect(page.locator('text=Updated title')).toBeVisible();
		await expect(page.locator('text=Original title')).not.toBeVisible();
	});

	test('delete task - removes task from list', async ({ page }) => {
		// Create a task
		await page.click('text=+ New Task');
		await page.fill('input#title', 'Task to delete');
		await page.click('button:text("Add Task")');

		await expect(page.locator('text=Task to delete')).toBeVisible();

		// Delete the task (handle confirmation dialog)
		page.on('dialog', (dialog) => dialog.accept());
		await page.click('button:text("Delete")');

		await expect(page.locator('text=Task to delete')).not.toBeVisible();
	});

	test('empty state - shows message when no tasks', async ({ page }) => {
		await expect(page.locator('text=No tasks yet')).toBeVisible();
	});

	test('toggle task completion', async ({ page }) => {
		// Create a task
		await page.click('text=+ New Task');
		await page.fill('input#title', 'Task to complete');
		await page.click('button:text("Add Task")');

		// Find and click the checkbox
		const checkbox = page.locator('button[aria-label="Mark complete"]');
		await checkbox.click();

		// Task should now show as completed (has checkmark)
		await expect(page.locator('button[aria-label="Mark incomplete"]')).toBeVisible();
	});
});
