<script lang="ts">
	import { taskStore } from '$lib/stores/tasks';
	import TaskCard from './TaskCard.svelte';

	interface Task {
		id: string;
		title: string;
		description: string | null;
		is_completed: boolean;
		created_at: string;
		updated_at: string;
	}

	let { onEdit }: { onEdit: (task: Task) => void } = $props();

	const tasks = $derived(taskStore.filteredTasks());
</script>

{#if taskStore.loading}
	<div class="flex items-center justify-center py-8">
		<span class="text-muted-foreground">Loading tasks...</span>
	</div>
{:else if tasks.length === 0}
	<div class="rounded-lg border bg-card p-8 text-center">
		<p class="text-muted-foreground">
			{#if taskStore.filter === 'all'}
				No tasks yet. Create your first task above!
			{:else if taskStore.filter === 'active'}
				No active tasks. Great job!
			{:else}
				No completed tasks yet.
			{/if}
		</p>
	</div>
{:else}
	<div class="space-y-3">
		{#each tasks as task (task.id)}
			<TaskCard {task} {onEdit} />
		{/each}
	</div>
{/if}
