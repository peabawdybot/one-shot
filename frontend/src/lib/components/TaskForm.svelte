<script lang="ts">
	import { taskStore } from '$lib/stores/tasks';

	interface Task {
		id: string;
		title: string;
		description: string | null;
		is_completed: boolean;
	}

	let {
		editTask = null,
		onClose,
	}: {
		editTask?: Task | null;
		onClose: () => void;
	} = $props();

	let title = $state(editTask?.title ?? '');
	let description = $state(editTask?.description ?? '');
	let loading = $state(false);

	const isEditing = $derived(editTask !== null);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (!title.trim()) return;

		loading = true;

		let success: boolean;
		if (isEditing && editTask) {
			success = await taskStore.updateTask(editTask.id, {
				title: title.trim(),
				description: description.trim() || undefined,
			});
		} else {
			success = await taskStore.createTask({
				title: title.trim(),
				description: description.trim() || undefined,
			});
		}

		if (success) {
			title = '';
			description = '';
			onClose();
		}

		loading = false;
	}
</script>

<form onsubmit={handleSubmit} class="rounded-lg border bg-card p-4">
	<h3 class="mb-4 font-medium">{isEditing ? 'Edit Task' : 'New Task'}</h3>

	{#if taskStore.error}
		<div class="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
			{taskStore.error}
		</div>
	{/if}

	<div class="space-y-4">
		<div>
			<label for="title" class="mb-1 block text-sm font-medium">Title</label>
			<input
				type="text"
				id="title"
				bind:value={title}
				required
				class="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
				placeholder="What needs to be done?"
			/>
		</div>

		<div>
			<label for="description" class="mb-1 block text-sm font-medium">Description (optional)</label>
			<textarea
				id="description"
				bind:value={description}
				rows="2"
				class="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
				placeholder="Add more details..."
			></textarea>
		</div>

		<div class="flex gap-2">
			<button
				type="submit"
				disabled={loading || !title.trim()}
				class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
			>
				{loading ? 'Saving...' : isEditing ? 'Update' : 'Add Task'}
			</button>
			<button
				type="button"
				onclick={onClose}
				class="rounded-md bg-secondary px-4 py-2 text-sm font-medium hover:bg-secondary/80"
			>
				Cancel
			</button>
		</div>
	</div>
</form>
