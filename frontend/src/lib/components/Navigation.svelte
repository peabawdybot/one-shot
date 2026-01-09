<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';

	async function handleLogout() {
		await auth.logout();
		goto('/login');
	}
</script>

<nav class="border-b bg-background">
	<div class="container mx-auto flex h-16 items-center justify-between px-4">
		<a href="/dashboard" class="text-xl font-bold">Task Manager</a>

		{#if auth.isAuthenticated}
			<div class="flex items-center gap-4">
				<a href="/dashboard" class="text-sm hover:underline">Dashboard</a>

				{#if auth.isAdmin}
					<a href="/admin" class="text-sm hover:underline">Admin</a>
				{/if}

				<span class="text-sm text-muted-foreground">{auth.user?.email}</span>

				<button
					onclick={handleLogout}
					class="rounded-md bg-secondary px-3 py-1.5 text-sm hover:bg-secondary/80"
				>
					Logout
				</button>
			</div>
		{:else}
			<div class="flex items-center gap-4">
				<a href="/login" class="text-sm hover:underline">Login</a>
				<a
					href="/register"
					class="rounded-md bg-primary px-3 py-1.5 text-sm text-primary-foreground hover:bg-primary/90"
				>
					Register
				</a>
			</div>
		{/if}
	</div>
</nav>
