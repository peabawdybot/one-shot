<script lang="ts">
	import { taskStore } from '$lib/stores/tasks';

	const filters = [
		{ value: 'all' as const, label: 'All' },
		{ value: 'active' as const, label: 'Active' },
		{ value: 'completed' as const, label: 'Completed' },
	];
</script>

<div class="flex gap-1 rounded-lg bg-muted p-1">
	{#each filters as filter}
		<button
			onclick={() => taskStore.setFilter(filter.value)}
			class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors {taskStore.filter ===
			filter.value
				? 'bg-background text-foreground shadow-sm'
				: 'text-muted-foreground hover:text-foreground'}"
		>
			{filter.label}
		</button>
	{/each}
</div>
