<script lang="ts">
	import { taskStore } from '$lib/stores/tasks';

	interface Task {
		id: string;
		title: string;
		description: string | null;
		is_completed: boolean;
		created_at: string;
		updated_at: string;
	}

	let { task, onEdit }: { task: Task; onEdit: (task: Task) => void } = $props();
	let deleting = $state(false);

	async function handleToggle() {
		await taskStore.toggleComplete(task.id);
	}

	async function handleDelete() {
		if (!confirm('Are you sure you want to delete this task?')) return;
		deleting = true;
		await taskStore.deleteTask(task.id);
		deleting = false;
	}
</script>

<div
	class="flex items-start gap-3 rounded-lg border bg-card p-4 transition-colors {task.is_completed
		? 'opacity-60'
		: ''}"
>
	<button
		onclick={handleToggle}
		class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border {task.is_completed
			? 'border-primary bg-primary text-primary-foreground'
			: 'border-input hover:border-primary'}"
		aria-label={task.is_completed ? 'Mark incomplete' : 'Mark complete'}
	>
		{#if task.is_completed}
			<svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
			</svg>
		{/if}
	</button>

	<div class="min-w-0 flex-1">
		<h3 class="font-medium {task.is_completed ? 'line-through text-muted-foreground' : ''}">
			{task.title}
		</h3>
		{#if task.description}
			<p class="mt-1 text-sm text-muted-foreground">{task.description}</p>
		{/if}
	</div>

	<div class="flex shrink-0 gap-2">
		<button
			onclick={() => onEdit(task)}
			class="rounded px-2 py-1 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
		>
			Edit
		</button>
		<button
			onclick={handleDelete}
			disabled={deleting}
			class="rounded px-2 py-1 text-sm text-destructive hover:bg-destructive/10 disabled:opacity-50"
		>
			{deleting ? '...' : 'Delete'}
		</button>
	</div>
</div>
