<script lang="ts">
	import { onMount } from 'svelte';
	import { taskStore } from '$lib/stores/tasks';
	import TaskList from '$lib/components/TaskList.svelte';
	import TaskForm from '$lib/components/TaskForm.svelte';
	import TaskFilter from '$lib/components/TaskFilter.svelte';

	interface Task {
		id: string;
		title: string;
		description: string | null;
		is_completed: boolean;
		created_at: string;
		updated_at: string;
	}

	let showForm = $state(false);
	let editingTask = $state<Task | null>(null);

	onMount(() => {
		taskStore.fetchTasks();
	});

	function handleEdit(task: Task) {
		editingTask = task;
		showForm = true;
	}

	function handleCloseForm() {
		showForm = false;
		editingTask = null;
		taskStore.clearError();
	}

	function handleNewTask() {
		editingTask = null;
		showForm = true;
	}
</script>

<svelte:head>
	<title>Dashboard - Task Manager</title>
</svelte:head>

<div>
	<div class="mb-8 flex items-center justify-between">
		<h1 class="text-2xl font-bold">My Tasks</h1>
		<div class="flex items-center gap-4">
			<TaskFilter />
			{#if !showForm}
				<button
					onclick={handleNewTask}
					class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
				>
					+ New Task
				</button>
			{/if}
		</div>
	</div>

	{#if showForm}
		<div class="mb-6">
			<TaskForm editTask={editingTask} onClose={handleCloseForm} />
		</div>
	{/if}

	<TaskList onEdit={handleEdit} />
</div>
