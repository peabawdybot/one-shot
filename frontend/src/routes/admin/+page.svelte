<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import UserTable from '$lib/components/UserTable.svelte';

	interface AdminUser {
		id: string;
		email: string;
		role: 'user' | 'admin';
		is_active: boolean;
		created_at: string;
		last_login_at: string | null;
		task_count: number;
	}

	interface UserListResponse {
		users: AdminUser[];
		total: number;
	}

	let users = $state<AdminUser[]>([]);
	let total = $state(0);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(() => {
		fetchUsers();
	});

	async function fetchUsers() {
		loading = true;
		error = null;

		const response = await api.get<UserListResponse>('/admin/users');

		if (response.error) {
			error = response.error;
		} else if (response.data) {
			users = response.data.users;
			total = response.data.total;
		}

		loading = false;
	}
</script>

<svelte:head>
	<title>Admin Panel - Task Manager</title>
</svelte:head>

<div>
	<div class="mb-8">
		<h1 class="text-2xl font-bold">Admin Panel</h1>
		<p class="text-muted-foreground">Manage users and view platform statistics</p>
	</div>

	{#if error}
		<div class="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
			{error}
		</div>
	{/if}

	<div class="mb-4 rounded-lg border bg-card p-4">
		<p class="text-sm text-muted-foreground">Total Users: <span class="font-medium text-foreground">{total}</span></p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-8">
			<span class="text-muted-foreground">Loading users...</span>
		</div>
	{:else if users.length === 0}
		<div class="rounded-lg border bg-card p-8 text-center">
			<p class="text-muted-foreground">No users found.</p>
		</div>
	{:else}
		<UserTable {users} onStatusChange={fetchUsers} />
	{/if}
</div>
